#!/usr/bin/env python3
"""
방과 후 생존 - EnemySpawner 데모 게임
=====================================

마우스로 이동, 자동 공격하는 플레이어로 웨이브별 적들을 상대하는 게임입니다.

조작법:
- 마우스: 이동 (플레이어가 마우스를 향해 이동)
- F키: 보스 강제 스폰 (디버그용)
- C키: 모든 적 제거 (디버그용)
- ESC: 게임 종료

게임 특징:
- 웨이브별 적 타입과 난이도 변화
- 실시간 통계 표시
- 40+ FPS 성능 최적화
- ECS 아키텍처 기반 적 관리
"""

import pygame
import random
import math
from typing import List, Optional

# ECS 시스템 임포트
from src.core.entity_manager import EntityManager
from src.systems.enemy_spawner import EnemySpawner, SpawnWave
from src.components.position_component import PositionComponent
from src.components.health_component import HealthComponent
from src.components.enums import EnemyType

# AI-NOTE : 2025-01-13 완전한 게임 데모 구현
# - 이유: EnemySpawner 시스템의 모든 기능을 시연할 수 있는 완전한 게임 필요
# - 요구사항: 직관적인 조작, 시각적 피드백, 성능 최적화, 게임성 확보
# - 히스토리: main_with_spawner.py를 기반으로 완전한 게임 경험으로 확장

# 게임 초기화
pygame.init()
pygame.mixer.init()

# 게임 설정
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 700
FPS = 60

# 색상 정의
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)
PURPLE = (128, 0, 128)
CYAN = (0, 255, 255)
PINK = (255, 192, 203)
GRAY = (128, 128, 128)
DARK_RED = (139, 0, 0)
GOLD = (255, 215, 0)

# 화면 및 시계 설정
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("방과 후 생존 - EnemySpawner 데모")
clock = pygame.time.Clock()

class Particle:
    """시각적 효과용 파티클 클래스"""
    def __init__(self, x: float, y: float, color: tuple, velocity: tuple, lifetime: float):
        self.x = x
        self.y = y
        self.color = color
        self.vx, self.vy = velocity
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self.size = random.randint(2, 5)
    
    def update(self, delta_time: float) -> bool:
        """파티클 업데이트, 수명이 다하면 False 반환"""
        self.x += self.vx * delta_time
        self.y += self.vy * delta_time
        self.lifetime -= delta_time
        
        # 중력 효과
        self.vy += 200 * delta_time
        
        return self.lifetime > 0
    
    def draw(self, surf: pygame.Surface):
        """파티클 그리기"""
        if self.lifetime <= 0:
            return
        
        # 수명에 따른 알파값 계산
        alpha_ratio = self.lifetime / self.max_lifetime
        alpha = int(255 * alpha_ratio)
        
        # 색상에 알파 적용
        color_with_alpha = (*self.color[:3], alpha)
        size = max(1, int(self.size * alpha_ratio))
        
        pygame.draw.circle(surf, self.color[:3], (int(self.x), int(self.y)), size)

class Player:
    """플레이어 클래스"""
    def __init__(self):
        self.x = SCREEN_WIDTH // 2
        self.y = SCREEN_HEIGHT // 2
        self.size = 25
        self.max_health = 100
        self.health = 100
        self.speed = 300.0  # 픽셀/초
        
        # 공격 관련
        self.attack_damage = 25
        self.attack_speed = 4.0  # 초당 공격 횟수
        self.attack_cooldown = 0.0
        
        # 무적 시간
        self.invulnerable = False
        self.invulnerable_duration = 1.0  # 초
        self.invulnerable_timer = 0.0
        
        # 경험치 및 레벨
        self.exp = 0
        self.level = 1
        self.exp_to_next = 100
        
        # 점수
        self.score = 0
        
        # 시각적 효과
        self.hit_flash = 0.0
    
    def update(self, delta_time: float, mouse_pos: tuple):
        """플레이어 업데이트"""
        # 마우스 방향으로 이동
        dx = mouse_pos[0] - self.x
        dy = mouse_pos[1] - self.y
        distance = math.sqrt(dx*dx + dy*dy)
        
        if distance > 5:  # 지터링 방지
            # 정규화된 방향
            dir_x = dx / distance
            dir_y = dy / distance
            
            # 속도 적용
            move_distance = self.speed * delta_time
            self.x += dir_x * move_distance
            self.y += dir_y * move_distance
        
        # 화면 경계 체크
        self.x = max(self.size, min(SCREEN_WIDTH - self.size, self.x))
        self.y = max(self.size, min(SCREEN_HEIGHT - self.size, self.y))
        
        # 공격 쿨다운
        if self.attack_cooldown > 0:
            self.attack_cooldown -= delta_time
        
        # 무적 시간
        if self.invulnerable:
            self.invulnerable_timer -= delta_time
            if self.invulnerable_timer <= 0:
                self.invulnerable = False
        
        # 시각적 효과 감소
        if self.hit_flash > 0:
            self.hit_flash -= delta_time * 3
    
    def can_attack(self) -> bool:
        """공격 가능한지 확인"""
        return self.attack_cooldown <= 0
    
    def attack(self) -> None:
        """공격 실행"""
        if self.can_attack():
            self.attack_cooldown = 1.0 / self.attack_speed
    
    def take_damage(self, amount: int) -> bool:
        """피해를 받음, 사망 시 True 반환"""
        if self.invulnerable:
            return False
        
        self.health -= amount
        self.invulnerable = True
        self.invulnerable_timer = self.invulnerable_duration
        self.hit_flash = 1.0
        
        if self.health <= 0:
            self.health = 0
            return True  # 사망
        return False
    
    def gain_exp(self, amount: int):
        """경험치 획득"""
        self.exp += amount
        while self.exp >= self.exp_to_next:
            self.level_up()
    
    def level_up(self):
        """레벨업"""
        self.exp -= self.exp_to_next
        self.level += 1
        self.exp_to_next = int(self.exp_to_next * 1.5)
        
        # 스탯 증가
        self.max_health += 10
        self.health = min(self.max_health, self.health + 20)  # 레벨업 시 체력 회복
        self.attack_damage += 2
        self.attack_speed *= 1.1
        
        print(f"🎉 레벨업! 레벨 {self.level}")
    
    def draw(self, surf: pygame.Surface):
        """플레이어 그리기"""
        # 무적 상태일 때 깜빡임 효과
        if self.invulnerable and int(self.invulnerable_timer * 10) % 2:
            return  # 깜빡임으로 그리지 않음
        
        # 피해 받았을 때 붉은 효과
        color = GREEN
        if self.hit_flash > 0:
            flash_intensity = int(self.hit_flash * 255)
            color = (min(255, GREEN[0] + flash_intensity), GREEN[1], GREEN[2])
        
        # 플레이어 그리기 (삼각형)
        angle = math.atan2(pygame.mouse.get_pos()[1] - self.y, 
                          pygame.mouse.get_pos()[0] - self.x)
        
        # 삼각형 꼭짓점 계산
        points = []
        for i in range(3):
            point_angle = angle + (i * 2 * math.pi / 3)
            px = self.x + math.cos(point_angle) * self.size
            py = self.y + math.sin(point_angle) * self.size
            points.append((px, py))
        
        pygame.draw.polygon(surf, color, points)
        pygame.draw.polygon(surf, WHITE, points, 2)
        
        # 레벨 표시
        font = pygame.font.Font(None, 20)
        level_text = font.render(str(self.level), True, WHITE)
        text_rect = level_text.get_rect(center=(self.x, self.y))
        surf.blit(level_text, text_rect)

class Projectile:
    """투사체 클래스"""
    def __init__(self, x: float, y: float, target_x: float, target_y: float, damage: int):
        self.x = x
        self.y = y
        self.damage = damage
        self.speed = 500.0  # 픽셀/초
        self.size = 5
        self.lifetime = 2.0  # 최대 수명
        
        # 방향 계산
        dx = target_x - x
        dy = target_y - y
        distance = math.sqrt(dx*dx + dy*dy)
        
        if distance > 0:
            self.vx = (dx / distance) * self.speed
            self.vy = (dy / distance) * self.speed
        else:
            self.vx = self.vy = 0
    
    def update(self, delta_time: float) -> bool:
        """투사체 업데이트, 수명이 다하면 False 반환"""
        self.x += self.vx * delta_time
        self.y += self.vy * delta_time
        self.lifetime -= delta_time
        
        # 화면 밖으로 나가면 제거
        if (self.x < -50 or self.x > SCREEN_WIDTH + 50 or 
            self.y < -50 or self.y > SCREEN_HEIGHT + 50):
            return False
        
        return self.lifetime > 0
    
    def draw(self, surf: pygame.Surface):
        """투사체 그리기"""
        pygame.draw.circle(surf, YELLOW, (int(self.x), int(self.y)), self.size)
        pygame.draw.circle(surf, WHITE, (int(self.x), int(self.y)), self.size, 1)

class EnemySprite:
    """ECS Enemy를 시각적으로 표현하는 스프라이트"""
    def __init__(self, enemy, entity_manager: EntityManager):
        self.enemy = enemy
        self.entity_manager = entity_manager
        self.alive = True
        
        # 적 타입별 시각적 설정
        self.setup_visuals()
        
        # 시각적 효과
        self.hit_flash = 0.0
        self.scale_effect = 1.0
        
        # AI 관련
        self.last_direction_change = 0.0
        self.wander_angle = random.uniform(0, 2 * math.pi)
    
    def setup_visuals(self):
        """적 타입별 시각적 설정"""
        type_configs = {
            EnemyType.KOREAN_TEACHER: {
                'color': RED,
                'size': 20,
                'name_short': '국어',
                'trail_color': (255, 100, 100)
            },
            EnemyType.MATH_TEACHER: {
                'color': BLUE, 
                'size': 18,
                'name_short': '수학',
                'trail_color': (100, 100, 255)
            },
            EnemyType.PRINCIPAL: {
                'color': PURPLE,
                'size': 35,
                'name_short': '교장',
                'trail_color': (200, 100, 200)
            }
        }
        
        config = type_configs.get(self.enemy.enemy_type, type_configs[EnemyType.KOREAN_TEACHER])
        self.color = config['color']
        self.size = config['size']
        self.name_short = config['name_short']
        self.trail_color = config['trail_color']
    
    def get_position(self) -> tuple:
        """ECS 엔티티의 위치 반환"""
        if not self.enemy.entity:
            return (0, 0)
        
        pos_comp = self.entity_manager.get_component(self.enemy.entity.id, PositionComponent)
        if pos_comp:
            return (pos_comp.x, pos_comp.y)
        return (0, 0)
    
    def set_position(self, x: float, y: float):
        """ECS 엔티티의 위치 설정"""
        if not self.enemy.entity:
            return
        
        pos_comp = self.entity_manager.get_component(self.enemy.entity.id, PositionComponent)
        if pos_comp:
            pos_comp.x = x
            pos_comp.y = y
    
    def update(self, delta_time: float, player_pos: tuple, current_time: float) -> List[Particle]:
        """적 업데이트 및 파티클 생성"""
        particles = []
        
        # 생존 확인
        if not self.enemy.is_alive():
            self.alive = False
            # 사망 파티클 생성
            pos = self.get_position()
            for _ in range(10):
                particles.append(Particle(
                    pos[0] + random.uniform(-self.size, self.size),
                    pos[1] + random.uniform(-self.size, self.size),
                    self.color,
                    (random.uniform(-100, 100), random.uniform(-200, -50)),
                    random.uniform(0.5, 1.5)
                ))
            return particles
        
        # 시각적 효과 업데이트
        if self.hit_flash > 0:
            self.hit_flash -= delta_time * 4
        
        if self.scale_effect != 1.0:
            self.scale_effect += (1.0 - self.scale_effect) * delta_time * 5
        
        # 간단한 플레이어 추적 AI
        self.update_ai(delta_time, player_pos, current_time)
        
        return particles
    
    def update_ai(self, delta_time: float, player_pos: tuple, current_time: float):
        """간단한 AI 업데이트"""
        pos = self.get_position()
        px, py = player_pos
        
        # 플레이어와의 거리 및 방향 계산
        dx = px - pos[0]
        dy = py - pos[1]
        distance = math.sqrt(dx*dx + dy*dy)
        
        if distance > 5:
            # 적 타입별 이동 패턴
            speed = self.enemy.enemy_type.base_speed * 60  # 초당 픽셀로 변환
            
            if self.enemy.enemy_type == EnemyType.MATH_TEACHER:
                # 수학선생님: 빠른 직선 이동
                dir_x = dx / distance
                dir_y = dy / distance
                new_x = pos[0] + dir_x * speed * delta_time
                new_y = pos[1] + dir_y * speed * delta_time
                
            elif self.enemy.enemy_type == EnemyType.KOREAN_TEACHER:
                # 국어선생님: 느린 이동, 가끔 멈춤
                if current_time - self.last_direction_change > 2.0:
                    self.last_direction_change = current_time
                    if random.random() < 0.3:  # 30% 확률로 잠깐 멈춤
                        speed *= 0.2
                
                dir_x = dx / distance
                dir_y = dy / distance
                new_x = pos[0] + dir_x * speed * delta_time
                new_y = pos[1] + dir_y * speed * delta_time
                
            else:  # 교장선생님
                # 교장선생님: 복잡한 이동 패턴 (원형 궤도 + 접근)
                if current_time - self.last_direction_change > 3.0:
                    self.last_direction_change = current_time
                    self.wander_angle = random.uniform(0, 2 * math.pi)
                
                # 원형 움직임 + 플레이어 접근
                orbit_x = math.cos(current_time * 2 + self.wander_angle) * 50
                orbit_y = math.sin(current_time * 2 + self.wander_angle) * 50
                
                target_x = px + orbit_x
                target_y = py + orbit_y
                
                dx = target_x - pos[0]
                dy = target_y - pos[1]
                new_distance = math.sqrt(dx*dx + dy*dy)
                
                if new_distance > 5:
                    dir_x = dx / new_distance
                    dir_y = dy / new_distance
                    new_x = pos[0] + dir_x * speed * delta_time
                    new_y = pos[1] + dir_y * speed * delta_time
                else:
                    new_x, new_y = pos
            
            # 화면 경계 체크
            new_x = max(self.size, min(SCREEN_WIDTH - self.size, new_x))
            new_y = max(self.size, min(SCREEN_HEIGHT - self.size, new_y))
            
            self.set_position(new_x, new_y)
    
    def take_damage(self, amount: int) -> bool:
        """피해를 받음"""
        self.hit_flash = 1.0
        self.scale_effect = 1.3
        
        is_dead = self.enemy.take_damage(amount)
        return is_dead
    
    def check_collision_with_point(self, x: float, y: float, radius: float = 0) -> bool:
        """점과의 충돌 확인"""
        pos = self.get_position()
        dx = x - pos[0]
        dy = y - pos[1]
        distance = math.sqrt(dx*dx + dy*dy)
        return distance < (self.size + radius)
    
    def draw(self, surf: pygame.Surface):
        """적 그리기"""
        if not self.alive:
            return
        
        pos = self.get_position()
        
        # 피해 효과
        color = self.color
        if self.hit_flash > 0:
            flash_intensity = int(self.hit_flash * 100)
            color = (
                min(255, color[0] + flash_intensity),
                max(0, color[1] - flash_intensity//2),
                max(0, color[2] - flash_intensity//2)
            )
        
        # 크기 효과
        draw_size = int(self.size * self.scale_effect)
        
        # 적 본체 그리기
        pygame.draw.circle(surf, color, (int(pos[0]), int(pos[1])), draw_size)
        pygame.draw.circle(surf, WHITE, (int(pos[0]), int(pos[1])), draw_size, 2)
        
        # 적 타입 표시
        font = pygame.font.Font(None, 16 if draw_size < 25 else 20)
        text = font.render(self.name_short, True, WHITE)
        text_rect = text.get_rect(center=pos)
        surf.blit(text, text_rect)
        
        # 보스급은 체력바 표시
        if self.enemy.enemy_type == EnemyType.PRINCIPAL:
            self.draw_health_bar(surf, pos)
    
    def draw_health_bar(self, surf: pygame.Surface, pos: tuple):
        """체력바 그리기 (보스용)"""
        if not self.enemy.entity:
            return
        
        health_comp = self.entity_manager.get_component(self.enemy.entity.id, HealthComponent)
        if not health_comp:
            return
        
        bar_width = self.size * 2
        bar_height = 4
        bar_x = pos[0] - bar_width // 2
        bar_y = pos[1] - self.size - 10
        
        # 배경바
        pygame.draw.rect(surf, DARK_RED, (bar_x, bar_y, bar_width, bar_height))
        
        # 체력바
        health_ratio = health_comp.current / health_comp.maximum
        fill_width = int(bar_width * health_ratio)
        pygame.draw.rect(surf, GREEN, (bar_x, bar_y, fill_width, bar_height))
        
        # 테두리
        pygame.draw.rect(surf, WHITE, (bar_x, bar_y, bar_width, bar_height), 1)

class Game:
    """메인 게임 클래스"""
    def __init__(self):
        # ECS 시스템
        self.entity_manager = EntityManager()
        self.enemy_spawner = EnemySpawner(self.entity_manager)
        
        # 게임 객체들
        self.player = Player()
        self.enemy_sprites: List[EnemySprite] = []
        self.projectiles: List[Projectile] = []
        self.particles: List[Particle] = []
        
        # 게임 상태
        self.running = True
        self.game_over = False
        self.paused = False
        self.start_time = pygame.time.get_ticks()
        
        # 자동 공격 타겟팅
        self.auto_attack_timer = 0.0
        
        # 폰트
        self.font_small = pygame.font.Font(None, 24)
        self.font_medium = pygame.font.Font(None, 36)
        self.font_large = pygame.font.Font(None, 48)
        
        # 사운드 (임시로 텍스트 알림)
        self.last_wave = SpawnWave.EARLY_GAME
        
        print("🎮 게임 시작!")
        print("조작법: 마우스로 이동, F키로 보스 스폰, C키로 적 제거, ESC로 종료")
    
    def handle_events(self):
        """이벤트 처리"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_f:
                    # 보스 강제 스폰
                    boss = self.enemy_spawner.force_spawn_boss()
                    if boss:
                        boss_sprite = EnemySprite(boss, self.entity_manager)
                        self.enemy_sprites.append(boss_sprite)
                        print("💀 보스 강제 소환!")
                elif event.key == pygame.K_c:
                    # 모든 적 제거
                    removed_count = self.enemy_spawner.clear_all_enemies()
                    self.enemy_sprites.clear()
                    print(f"🧹 모든 적 제거: {removed_count}개")
                elif event.key == pygame.K_SPACE:
                    # 일시정지
                    self.paused = not self.paused
    
    def find_nearest_enemy(self) -> Optional[EnemySprite]:
        """가장 가까운 적 찾기"""
        if not self.enemy_sprites:
            return None
        
        nearest_enemy = None
        min_distance = float('inf')
        
        player_pos = (self.player.x, self.player.y)
        
        for enemy in self.enemy_sprites:
            if not enemy.alive:
                continue
            
            enemy_pos = enemy.get_position()
            dx = enemy_pos[0] - player_pos[0]
            dy = enemy_pos[1] - player_pos[1]
            distance = math.sqrt(dx*dx + dy*dy)
            
            if distance < min_distance:
                min_distance = distance
                nearest_enemy = enemy
        
        return nearest_enemy
    
    def update(self, delta_time: float):
        """게임 업데이트"""
        if self.paused or self.game_over:
            return
        
        current_time = pygame.time.get_ticks() / 1000.0
        
        # 플레이어 업데이트
        mouse_pos = pygame.mouse.get_pos()
        self.player.update(delta_time, mouse_pos)
        
        # 자동 공격
        self.auto_attack_timer -= delta_time
        if self.auto_attack_timer <= 0 and self.player.can_attack():
            target = self.find_nearest_enemy()
            if target and target.alive:
                target_pos = target.get_position()
                # 공격 범위 체크 (200픽셀)
                dx = target_pos[0] - self.player.x
                dy = target_pos[1] - self.player.y
                distance = math.sqrt(dx*dx + dy*dy)
                
                if distance <= 200:
                    projectile = Projectile(
                        self.player.x, self.player.y,
                        target_pos[0], target_pos[1],
                        self.player.attack_damage
                    )
                    self.projectiles.append(projectile)
                    self.player.attack()
                    self.auto_attack_timer = 0.1  # 다음 공격 후보 검색 간격
        
        # 적 스포너 업데이트
        new_enemies = self.enemy_spawner.update(delta_time)
        for enemy in new_enemies:
            enemy_sprite = EnemySprite(enemy, self.entity_manager)
            self.enemy_sprites.append(enemy_sprite)
        
        # 웨이브 변경 알림
        current_wave = self.enemy_spawner.current_wave
        if current_wave != self.last_wave:
            print(f"🌊 웨이브 변경: {self.last_wave.display_name} → {current_wave.display_name}")
            self.last_wave = current_wave
            
            # 웨이브 변경 파티클 효과
            for _ in range(20):
                self.particles.append(Particle(
                    SCREEN_WIDTH // 2 + random.uniform(-100, 100),
                    SCREEN_HEIGHT // 2 + random.uniform(-50, 50),
                    GOLD,
                    (random.uniform(-50, 50), random.uniform(-100, -50)),
                    2.0
                ))
        
        # 적 업데이트
        alive_enemies = []
        for enemy in self.enemy_sprites:
            if enemy.alive:
                new_particles = enemy.update(delta_time, (self.player.x, self.player.y), current_time)
                self.particles.extend(new_particles)
                alive_enemies.append(enemy)
            else:
                # 적 사망 시 경험치 및 점수 획득
                exp_gain = enemy.enemy.enemy_type.base_attack_power * 2
                score_gain = enemy.enemy.enemy_type.base_health
                self.player.gain_exp(exp_gain)
                self.player.score += score_gain
        
        self.enemy_sprites = alive_enemies
        
        # 투사체 업데이트
        active_projectiles = []
        for projectile in self.projectiles:
            if projectile.update(delta_time):
                active_projectiles.append(projectile)
        self.projectiles = active_projectiles
        
        # 충돌 검사: 투사체 vs 적
        for projectile in self.projectiles[:]:
            for enemy in self.enemy_sprites:
                if not enemy.alive:
                    continue
                
                if enemy.check_collision_with_point(projectile.x, projectile.y, projectile.size):
                    # 적에게 피해
                    is_dead = enemy.take_damage(projectile.damage)
                    
                    # 히트 파티클 생성
                    for _ in range(5):
                        self.particles.append(Particle(
                            projectile.x + random.uniform(-5, 5),
                            projectile.y + random.uniform(-5, 5),
                            YELLOW,
                            (random.uniform(-50, 50), random.uniform(-50, 50)),
                            0.5
                        ))
                    
                    # 투사체 제거
                    if projectile in self.projectiles:
                        self.projectiles.remove(projectile)
                    break
        
        # 충돌 검사: 플레이어 vs 적
        for enemy in self.enemy_sprites:
            if not enemy.alive:
                continue
            
            if enemy.check_collision_with_point(self.player.x, self.player.y, self.player.size):
                # 플레이어가 피해를 받음
                damage = enemy.enemy.enemy_type.base_attack_power
                is_dead = self.player.take_damage(damage)
                
                if is_dead:
                    self.game_over = True
                    print("💀 게임 오버!")
                
                # 피해 파티클
                for _ in range(8):
                    self.particles.append(Particle(
                        self.player.x + random.uniform(-self.player.size, self.player.size),
                        self.player.y + random.uniform(-self.player.size, self.player.size),
                        RED,
                        (random.uniform(-80, 80), random.uniform(-80, 80)),
                        1.0
                    ))
        
        # 파티클 업데이트
        active_particles = []
        for particle in self.particles:
            if particle.update(delta_time):
                active_particles.append(particle)
        self.particles = active_particles
    
    def draw_ui(self):
        """UI 그리기"""
        # 체력바
        bar_width = 200
        bar_height = 20
        bar_x = 20
        bar_y = 20
        
        # 체력바 배경
        pygame.draw.rect(screen, DARK_RED, (bar_x, bar_y, bar_width, bar_height))
        
        # 체력바
        health_ratio = self.player.health / self.player.max_health
        fill_width = int(bar_width * health_ratio)
        health_color = GREEN if health_ratio > 0.3 else RED
        pygame.draw.rect(screen, health_color, (bar_x, bar_y, fill_width, bar_height))
        
        # 체력바 테두리 및 텍스트
        pygame.draw.rect(screen, WHITE, (bar_x, bar_y, bar_width, bar_height), 2)
        health_text = self.font_small.render(f"HP: {self.player.health}/{self.player.max_health}", True, WHITE)
        screen.blit(health_text, (bar_x, bar_y + bar_height + 5))
        
        # 경험치바
        exp_bar_y = bar_y + 50
        exp_ratio = self.player.exp / self.player.exp_to_next
        exp_fill = int(bar_width * exp_ratio)
        
        pygame.draw.rect(screen, GRAY, (bar_x, exp_bar_y, bar_width, 10))
        pygame.draw.rect(screen, CYAN, (bar_x, exp_bar_y, exp_fill, 10))
        pygame.draw.rect(screen, WHITE, (bar_x, exp_bar_y, bar_width, 10), 1)
        
        exp_text = self.font_small.render(f"Level {self.player.level} - EXP: {self.player.exp}/{self.player.exp_to_next}", True, WHITE)
        screen.blit(exp_text, (bar_x, exp_bar_y + 15))
        
        # 점수
        score_text = self.font_medium.render(f"점수: {self.player.score}", True, WHITE)
        screen.blit(score_text, (bar_x, exp_bar_y + 45))
        
        # 스포너 통계 (우상단)
        stats = self.enemy_spawner.get_stats()
        stats_x = SCREEN_WIDTH - 300
        stats_y = 20
        
        stats_lines = [
            f"웨이브: {stats['current_wave']}",
            f"활성 적: {stats['active_enemies']}/{self.enemy_spawner.MAX_ENEMIES}",
            f"총 생성: {stats['total_spawned']}",
            f"다음 생성: {stats['next_spawn_in']:.1f}초 후"
        ]
        
        for i, line in enumerate(stats_lines):
            text = self.font_small.render(line, True, WHITE)
            screen.blit(text, (stats_x, stats_y + i * 25))
        
        # 현재 웨이브 강조
        wave_color = {
            SpawnWave.EARLY_GAME: GREEN,
            SpawnWave.MID_GAME: YELLOW,
            SpawnWave.LATE_GAME: ORANGE,
            SpawnWave.BOSS_PHASE: RED
        }.get(self.enemy_spawner.current_wave, WHITE)
        
        wave_text = self.font_medium.render(f"🌊 {stats['current_wave']}", True, wave_color)
        screen.blit(wave_text, (SCREEN_WIDTH // 2 - wave_text.get_width() // 2, 20))
        
        # FPS
        fps_text = self.font_small.render(f"FPS: {int(clock.get_fps())}", True, WHITE)
        screen.blit(fps_text, (20, SCREEN_HEIGHT - 30))
        
        # 조작법 안내 (하단)
        controls = "마우스: 이동 | F: 보스 스폰 | C: 적 제거 | SPACE: 일시정지 | ESC: 종료"
        controls_text = self.font_small.render(controls, True, GRAY)
        text_rect = controls_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 15))
        screen.blit(controls_text, text_rect)
    
    def draw_game_over(self):
        """게임 오버 화면"""
        # 반투명 오버레이
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill(BLACK)
        screen.blit(overlay, (0, 0))
        
        # 게임 오버 텍스트
        game_over_text = self.font_large.render("게임 오버", True, RED)
        text_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 100))
        screen.blit(game_over_text, text_rect)
        
        # 최종 통계
        stats_lines = [
            f"최종 점수: {self.player.score}",
            f"도달 레벨: {self.player.level}",
            f"웨이브: {self.enemy_spawner.current_wave.display_name}",
            f"처치한 적: {self.enemy_spawner.total_spawned - len(self.enemy_sprites)}",
            "",
            "ESC로 종료"
        ]
        
        for i, line in enumerate(stats_lines):
            if line:
                color = GOLD if "점수" in line else WHITE
                text = self.font_medium.render(line, True, color)
                text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 20 + i * 30))
                screen.blit(text, text_rect)
    
    def draw(self):
        """화면 그리기"""
        screen.fill(BLACK)
        
        # 배경 격자 (옵션)
        grid_size = 50
        for x in range(0, SCREEN_WIDTH, grid_size):
            pygame.draw.line(screen, (20, 20, 20), (x, 0), (x, SCREEN_HEIGHT))
        for y in range(0, SCREEN_HEIGHT, grid_size):
            pygame.draw.line(screen, (20, 20, 20), (0, y), (SCREEN_WIDTH, y))
        
        # 파티클 그리기 (배경)
        for particle in self.particles:
            particle.draw(screen)
        
        # 게임 객체 그리기
        if not self.game_over:
            self.player.draw(screen)
        
        for enemy in self.enemy_sprites:
            if enemy.alive:
                enemy.draw(screen)
        
        for projectile in self.projectiles:
            projectile.draw(screen)
        
        # UI 그리기
        self.draw_ui()
        
        # 일시정지 표시
        if self.paused:
            pause_text = self.font_large.render("일시정지 - SPACE로 재개", True, YELLOW)
            text_rect = pause_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            screen.blit(pause_text, text_rect)
        
        # 게임 오버 화면
        if self.game_over:
            self.draw_game_over()
        
        pygame.display.flip()
    
    def run(self):
        """메인 게임 루프"""
        while self.running:
            delta_time = clock.tick(FPS) / 1000.0
            
            self.handle_events()
            self.update(delta_time)
            self.draw()
        
        # 종료 통계
        stats = self.enemy_spawner.get_stats()
        print(f"\n🎯 게임 종료 통계")
        print(f"최종 점수: {self.player.score}")
        print(f"도달 레벨: {self.player.level}")
        print(f"최종 웨이브: {stats['current_wave']}")
        print(f"총 생성된 적: {stats['total_spawned']}")
        print(f"게임 시간: {(pygame.time.get_ticks() - self.start_time) // 1000}초")
        
        pygame.quit()

def main():
    """메인 함수"""
    try:
        game = Game()
        game.run()
    except Exception as e:
        print(f"게임 실행 중 오류: {e}")
        pygame.quit()

if __name__ == "__main__":
    main()