import pygame
import random

# ECS imports
from core.entity_manager import EntityManager
from systems.enemy_spawner import EnemySpawner
from components.position_component import PositionComponent
from components.health_component import HealthComponent

# AI-NOTE : 2025-01-13 EnemySpawner와 기존 pygame 시스템 통합 데모
# - 이유: ECS 기반 스포너 시스템을 기존 게임 루프에 통합하는 방법 시연
# - 요구사항: 기존 Player/Projectile pygame 시스템과 새로운 ECS Enemy 시스템 혼용
# - 히스토리: 완전한 ECS 전환 전 단계적 마이그레이션 접근법

# Initialize Pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# Create the screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("After School Survivors - With EnemySpawner")

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)

# Clock for FPS
clock = pygame.time.Clock()
FPS = 60

# Player class (기존 코드 유지)
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.original_image = pygame.Surface((50, 50), pygame.SRCALPHA)
        pygame.draw.polygon(self.original_image, GREEN, [(50, 25), (0, 0), (0, 50)])
        
        self.image = self.original_image.copy()
        self.rect = self.image.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2))
        
        self.max_health = 100
        self.health = 100
        self.speed = 5
        self.attack_speed = 4.0
        self.last_attack_time = 0
        
        self.invulnerable = False
        self.invulnerable_duration = 1000
        self.last_hit_time = 0

    def get_angle(self):
        mouse_pos = pygame.mouse.get_pos()
        direction = pygame.math.Vector2(mouse_pos) - self.rect.center
        return direction.angle_to(pygame.math.Vector2(1, 0))

    def attack(self, projectiles, all_sprites):
        now = pygame.time.get_ticks()
        attack_cooldown = 1000 / self.attack_speed
        if now - self.last_attack_time > attack_cooldown:
            self.last_attack_time = now
            angle = self.get_angle()
            projectile = Projectile(self.rect.center, angle)
            projectiles.add(projectile)
            all_sprites.add(projectile)

    def take_damage(self, amount):
        now = pygame.time.get_ticks()
        if not self.invulnerable:
            self.health -= amount
            self.invulnerable = True
            self.last_hit_time = now
            if self.health < 0:
                self.health = 0

    def update(self):
        now = pygame.time.get_ticks()
        if self.invulnerable and now - self.last_hit_time > self.invulnerable_duration:
            self.invulnerable = False

        angle = self.get_angle()
        self.image = pygame.transform.rotate(self.original_image, angle)
        self.rect = self.image.get_rect(center=self.rect.center)

        mouse_pos = pygame.mouse.get_pos()
        current_vector = pygame.math.Vector2(self.rect.center)
        target_vector = pygame.math.Vector2(mouse_pos)
        
        if target_vector.distance_to(current_vector) > 1:
            self.rect.center = current_vector.lerp(target_vector, 0.05)

        # Keep player on screen
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH
        if self.rect.top <= 0:
            self.rect.top = 0
        if self.rect.bottom >= SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT

# Projectile class (기존 코드 유지)
class Projectile(pygame.sprite.Sprite):
    def __init__(self, pos, angle):
        super().__init__()
        self.image = pygame.Surface((10, 5), pygame.SRCALPHA)
        self.image.fill(YELLOW)
        self.original_image = self.image
        self.rect = self.image.get_rect(center=pos)
        
        self.image = pygame.transform.rotate(self.original_image, angle)
        self.rect = self.image.get_rect(center=self.rect.center)
        self.velocity = pygame.math.Vector2(1, 0).rotate(-angle) * 10

    def update(self):
        self.rect.center += self.velocity
        if not screen.get_rect().colliderect(self.rect):
            self.kill()

# ECS Enemy 시각적 표현을 위한 pygame Sprite 어댑터
class EnemySprite(pygame.sprite.Sprite):
    """ECS Enemy 엔티티를 pygame.sprite로 렌더링하기 위한 어댑터"""
    
    def __init__(self, enemy, entity_manager):
        super().__init__()
        self.enemy = enemy
        self.entity_manager = entity_manager
        
        # 적 타입별 시각적 표현
        from components.enums import EnemyType
        colors = {
            EnemyType.KOREAN_TEACHER: RED,        # 국어선생님 - 빨간색
            EnemyType.MATH_TEACHER: BLUE,         # 수학선생님 - 파란색  
            EnemyType.PRINCIPAL: (128, 0, 128)    # 교장선생님 - 보라색
        }
        
        color = colors.get(enemy.enemy_type, RED)
        size = 40 if enemy.enemy_type.value == 2 else 30  # 보스는 더 크게
        
        self.image = pygame.Surface((size, size), pygame.SRCALPHA)
        pygame.draw.circle(self.image, color, (size//2, size//2), size//2)
        
        # 적 타입 표시 텍스트
        font = pygame.font.Font(None, 20)
        text = font.render(enemy.enemy_type.display_name[:2], True, WHITE)
        text_rect = text.get_rect(center=(size//2, size//2))
        self.image.blit(text, text_rect)
        
        self.rect = self.image.get_rect()
        self._update_position()
    
    def _update_position(self):
        """ECS 위치 컴포넌트에서 pygame rect 위치 동기화"""
        if not self.enemy.entity:
            return
            
        pos_comp = self.entity_manager.get_component(self.enemy.entity.id, PositionComponent)
        if pos_comp:
            self.rect.center = (pos_comp.x, pos_comp.y)
    
    def update(self):
        """매 프레임 위치 동기화 및 생존 상태 체크"""
        if not self.enemy.is_alive():
            self.kill()
            return
        
        self._update_position()
        
        # 간단한 플레이어 추적 AI (임시)
        if hasattr(self, '_player_pos'):
            pos_comp = self.entity_manager.get_component(self.enemy.entity.id, PositionComponent)
            if pos_comp:
                dx = self._player_pos[0] - pos_comp.x
                dy = self._player_pos[1] - pos_comp.y
                distance = (dx**2 + dy**2)**0.5
                
                if distance > 0:
                    speed = self.enemy.enemy_type.base_speed
                    pos_comp.x += (dx / distance) * speed
                    pos_comp.y += (dy / distance) * speed
    
    def set_player_position(self, player_pos):
        """플레이어 위치 설정 (AI용)"""
        self._player_pos = player_pos

def draw_health_bar(surf, x, y, pct):
    """체력바 그리기"""
    if pct < 0:
        pct = 0
    BAR_LENGTH = 100
    BAR_HEIGHT = 10
    fill = (pct / 100) * BAR_LENGTH
    outline_rect = pygame.Rect(x, y, BAR_LENGTH, BAR_HEIGHT)
    fill_rect = pygame.Rect(x, y, fill, BAR_HEIGHT)
    pygame.draw.rect(surf, GREEN, fill_rect)
    pygame.draw.rect(surf, WHITE, outline_rect, 2)

def draw_spawner_stats(surf, spawner, y_offset=50):
    """스포너 통계 표시"""
    stats = spawner.get_stats()
    font = pygame.font.Font(None, 24)
    
    lines = [
        f"웨이브: {stats['current_wave']}",
        f"활성 적: {stats['active_enemies']}/{spawner.MAX_ENEMIES}",
        f"총 생성: {stats['total_spawned']}",
        f"다음 생성: {stats['next_spawn_in']:.1f}초 후"
    ]
    
    for i, line in enumerate(lines):
        text = font.render(line, True, WHITE)
        surf.blit(text, (SCREEN_WIDTH - 250, y_offset + i * 25))

def show_game_over_screen():
    """게임 오버 화면"""
    screen.fill(BLACK)
    font = pygame.font.Font(None, 74)
    text = font.render("GAME OVER", True, RED)
    text_rect = text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2))
    screen.blit(text, text_rect)
    pygame.display.flip()
    pygame.time.wait(2000)

def main():
    """메인 게임 루프"""
    
    # AI-DEV : ECS와 pygame 시스템 혼합 사용 패턴
    # - 문제: 기존 pygame 코드를 완전히 바꾸지 않고 ECS 시스템 도입 필요
    # - 해결책: 어댑터 패턴으로 ECS Enemy를 pygame.sprite로 변환
    # - 주의사항: 성능상 완전 ECS로 전환하는 것이 이상적, 이는 임시 통합 방안
    
    # ECS 시스템 초기화
    entity_manager = EntityManager()
    enemy_spawner = EnemySpawner(entity_manager)
    
    # pygame sprite 그룹
    all_sprites = pygame.sprite.Group()
    projectiles = pygame.sprite.Group()
    enemy_sprites = pygame.sprite.Group()  # ECS Enemy 어댑터들
    
    # 플레이어 생성
    player = Player()
    all_sprites.add(player)
    
    # 게임 상태
    running = True
    game_over = False
    
    print("=== After School Survivors with EnemySpawner ===")
    print("마우스로 이동, 자동 공격")
    print("적 처치로 점수 획득, 웨이브 진행 관찰")
    print("F키: 보스 강제 스폰, C키: 모든 적 제거")
    
    while running:
        delta_time = clock.tick(FPS) / 1000.0  # 초 단위 델타 타임
        
        # 이벤트 처리
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_f:  # 보스 강제 스폰
                    boss = enemy_spawner.force_spawn_boss()
                    if boss:
                        boss_sprite = EnemySprite(boss, entity_manager)
                        enemy_sprites.add(boss_sprite)
                        all_sprites.add(boss_sprite)
                elif event.key == pygame.K_c:  # 모든 적 제거
                    enemy_spawner.clear_all_enemies()
                    for sprite in enemy_sprites:
                        sprite.kill()
                    enemy_sprites.empty()
        
        if not game_over:
            # 스포너 업데이트 - 새로운 적들 생성
            new_enemies = enemy_spawner.update(delta_time)
            
            # 새로 생성된 적들을 pygame sprite로 변환
            for enemy in new_enemies:
                enemy_sprite = EnemySprite(enemy, entity_manager)
                enemy_sprites.add(enemy_sprite)
                all_sprites.add(enemy_sprite)
            
            # 플레이어 위치를 모든 적 sprite에 전달 (AI용)
            player_pos = player.rect.center
            for enemy_sprite in enemy_sprites:
                enemy_sprite.set_player_position(player_pos)
            
            # 플레이어 자동 공격
            player.attack(projectiles, all_sprites)
            
            # 모든 sprite 업데이트
            all_sprites.update()
            
            # 충돌 검사: 적과 플레이어
            enemy_hits = pygame.sprite.spritecollide(player, enemy_sprites, False)
            for enemy_sprite in enemy_hits:
                player.take_damage(10)
                # ECS 적도 피해를 입게 처리
                enemy_sprite.enemy.take_damage(20)
                if player.health <= 0:
                    game_over = True
            
            # 충돌 검사: 투사체와 적
            projectile_hits = pygame.sprite.groupcollide(projectiles, enemy_sprites, True, False)
            for projectile, enemies in projectile_hits.items():
                for enemy_sprite in enemies:
                    # ECS 적에게 피해
                    is_dead = enemy_sprite.enemy.take_damage(25)
                    if is_dead:
                        print(f"{enemy_sprite.enemy.enemy_type.display_name} 처치!")
            
            # 죽은 적 sprite 정리 (EnemySprite.update()에서 자동 처리)
        
        # 화면 그리기
        screen.fill(BLACK)
        all_sprites.draw(screen)
        
        # UI 그리기
        draw_health_bar(screen, 10, 10, player.health)
        draw_spawner_stats(screen, enemy_spawner)
        
        # FPS 표시
        fps_text = pygame.font.Font(None, 36).render(f"FPS: {int(clock.get_fps())}", True, WHITE)
        screen.blit(fps_text, (10, SCREEN_HEIGHT - 40))
        
        if game_over:
            show_game_over_screen()
            running = False
        
        pygame.display.flip()
    
    # 종료 전 통계 출력
    final_stats = enemy_spawner.get_stats()
    print(f"\n=== 게임 종료 통계 ===")
    print(f"최종 웨이브: {final_stats['current_wave']}")
    print(f"총 생성된 적: {final_stats['total_spawned']}")
    print(f"마지막 활성 적: {final_stats['active_enemies']}")
    
    pygame.quit()

if __name__ == "__main__":
    main()