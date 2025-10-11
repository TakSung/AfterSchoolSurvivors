tests/total/system/test_enemy_system.py  에 enemy_movement_system 사용한 pygame 코드를 작성해줘. 10초마다 플러이어의 위치가 변경되고, 계속해서 적이 플레이어를 따라다니세 하는 프로그램을 작성해줘


# 3.8
-충돌/체력 시스템

### 문제점
-적이 안 없어짐(데이터는 사라졌지만 그림은 안 사라짐


경험치가 지금까지 얼마나 먹어졌는지 확인할 수 있는 바
누르면 바로 경험치가 들어오는 특정 키
53795963


# 5.1
src\entities\weapons.py
src\entities\item.py
src\systems\item_system.py

taskmaster task 5.1번을 테스트하기 위해서 tests/total/system/test_enemy_system.py 을 기반으로 tests/total/system/test_weapons_item.py 테스트를 만들어줘. 플레이어는 중간에 있고 1,2,3 키를 누르면 각각 야구배트, 농구공, 축구공이 나오게 해줘 . 공격은 마우스 방향대로 나가게 해줘

### ---
tests/total/system/test_weapons_item.py는 src\entities\weapons.py
src\entities\item.py
src\systems\item_system.py를 테스트 해볼려고 만든건야." 플레이어는 중간에 있고 1,2,3 키를 누르면 각각 야구배트, 농구공, 축구공이 나오게 해줘 . 공격은 마우스 방향대로 나가게 해줘"를 구현 한거야. 여기에 적들을 추가해주고.


tests/total/system/test_weapons_item.py는 src\entities\weapons.py
src\entities\item.py
src\systems\item_system.py를 테스트 해볼려고 만든건야. tests/total/system/test_weapons_item.py 기반으로 야구배트를 테스트할거야. 
여기에 적들을 추가해주고. 공격은 마우스 방향대로 나가게 해줘. 관련 정보를 제공할건데 야구배트 관련된 것만 확인해줘.


#### 3.4.1. 무기 아이템 (3종)
| 아이콘 | 이름 | 레벨별 강화 효과 |
| --- | --- | --- |
| ⚽️ | **축구공** | **Lv.1**: 1개 발사<br>**Lv.2**: 2개 발사<br>**Lv.3**: 튕기는 효과 추가 (1회)<br>**Lv.4**: 3개 발사<br>**Lv.5**: 튕기는 효과 강화 (2회) |
| 🏀 | **농구공** | **Lv.1**: 1개 발사 (관통 1명)<br>**Lv.2**: 발사 속도 20% 증가<br>**Lv.3**: 관통 +1명<br>**Lv.4**: 발사 속도 30% 증가<br>**Lv.5**: 관통 +2명 |
| ⚾️ | **야구 배트**| **Lv.1**: 전방 90도 범위 공격<br>**Lv.2**: 공격 속도 20% 증가<br>**Lv.3**: 범위 180도로 증가<br>**Lv.4**: 공격 속도 30% 증가<br>**Lv.5**: 범위 360도로 증가 |

#### 3.4.2. 능력 아이템 (4종)
| 아이콘 | 이름 | 레벨별 강화 효과 |
| --- | --- | --- |
| 👟 | **축구화** | **Lv.1**: 이동 속도 10% 증가<br>**Lv.2-5**: 레벨당 5% 추가 증가 |
| 🏀 | **농구화** | **Lv.1**: 10초마다 1초간 점프(무적/충돌무시)<br>**Lv.2-5**: 재사용 대기시간 1초씩 감소 |
| ⚫️ | **홍삼** | 획득 시 체력 50% 즉시 회복 (1회성 소모 아이템) |
| 🥛 | **우유** | 획득 시 체력 10% 즉시 회복 (1회성 소모 아이템) |



#### 3.4.3. 아이템 시너지
- **(축구공 + 축구화)**: 축구공 데미지 30% 증가
- **(야구 배트 + 농구화)**: 점프 착지 시, 야구 배트 자동 1회 휘두르기

### 3.5. 난이도 및 함정 시스템
- **난이도 곡선**:
  - 적 개체 수는 유지하되, 5분이 지날 때마다 적의 공격 속도/투사체 속도 30%씩 증가.
  - 5분/10분 경과 시 적 능력치(공격력/이동속도) 1.6배/2.0배 순차적 강화.
- **함정 시스템**:
  - 3분 경과 후부터 맵에 '압정' 함정 무작위 생성.
  - **효과**: 플레이어만 영향. 밟을 시 3초간 이동 속도 20% 감소.
  - **중첩**: 최대 3회까지 중첩 (최대 60% 감소).
  
  
  이걸 바탕으로 아이템을 구현해줘. 그리고 아이템을 각각 다른 키를 누르면 얻을수 욨게 해줘.



  지금 야구 배트라는 무기를 테스트 할려고 해. 공격은 마우스 방향대로 나가게 해줘. 1번을 누르면 자동으로 야구 배트가 추가되게 해줘. 데미지가 얼마나 들어갔는는지 무기가 지금 몇레벨인지도 표시해줘. 


  목적 : 야구 배트라는 무기를 테스트
  요구사항 : 
  1. 공격은 마우스 방향
  2. 1번 입력시 야구배트 추가(야구배트 아이템 획득)
  3. 야구배트로 인한 데미지 표시
  4. 야구배트 아이템 레벨 확인



1. 마우스 방향으로 공격'은 플레이어 위치에서 마우스 커서가 있는방향으로 공격이 나가는 것이 맞아. 배트를 휘두르는 모션과 함께 90도 내의 모든 적에게 피해를 줘.
2. 야구 배트를 이미 가지고 있는 상태에서 '1'번을 다시 누르면 야구배트의 레벨이 올라가. 
3. 데미지 숫자는 적 머리 위에 흰색 글씨로 나타나. 
4. 야구배트의 레벨은 화면 오른쪽 아래의 표시해줘. 레벨이 오르면서 상승하는 능력치는 나중에 추가할거야.       

 C:/Users/Rgorithm2/anaconda3/envs/as-game/python.exe c:/Users/Rgorithm2/Documents/jungwoosung/AfterSchoolSurvivors/tests/test_weapon_baseball_bat.py  


배트 모형
레벨에 따른 능력치 증가
스윙모션 
적 개수 (플레이어를 감싸게)
리셋 버튼

배트 모형, 스윙모션(충돌)
DATA, RENDER, 충돌, 

  src\systems\player_attack_system.py
  src\systems\collision_system.py
  src\systems\render_system.py
  src\entities\weapons.py


목표: 야구배트 렌더링하고 스윙 모션 추가
대상 파일:tests\total\system\test_baseball_bat_visual.py
여구사항: 
1. ecs system 적극사용
2. 마우스 방향을 기준으로 근접거리 90도 스윙모션 추가
3. player_attack_system 기반으로 자동공격 
4. 야구레 레벨 증가시 아래 규칙 따름 
   **Lv.1**: 전방 90도 범위 공격<br>**Lv.2**: 공격 속도 20% 증가<br>**Lv.3**: 범위 180도로 증가<br>**Lv.4**: 공격 속도 30% 증가<br>**Lv.5**: 범위 360도로 증가 |
준수사항: 
1. 아래있는 것 사용하기 
  src\systems\player_attack_system.py
  src\systems\collision_system.py
  src\systems\render_system.py
  src\entities\weapons.py
2. 주요 기능은 필요시 변경 가능
  src\entities\weapons.py
  src\systems\player_attack_system.py
3. 연관 기능은 변경이 필요하시 사용자에게 확인받기
  src\systems\collision_system.py
  src\systems\render_system.py

스윙이 보이지 않음. 스윙이 실행되지않음.
공격 키를 지정 후 표시

문제상황: 스윙이 보이지 않음.
상세설명: 스윙이 보이지 않음. 스윙이 실행행도 안되는 것으로 추정. 
문제 해결 방법: 
1. 문제 상황 분석
2. 작업계획 세우기


문제상황: 
1. 위 아래 공격 방향이 반대로 됨
2. 공격이 적에게 닿질 않음 - 데미지가 안들어감감




# 1011 목표
목표: main.py에 야구 빠따 기능 추가
현황: 야구 배트 뺴고 다른 기능은 추가 완료하여 건들 필요 없음
세부 요청: 
배트 스윙 모션 추가
3번키를 눌렀을때 야구배트가 소환하게 한다
다시누를때마 무기 레벨이 증가
BaseballBat, HitboxComponent 사용하여 기존 코드 업데이트
작업 순서
1. 목표 분석
2. 현황 분석
3. 작업 계획 세우기
4. 사용자 피드백 수용(작업 계획에 대한 피드백)
5. 기능 추가
6. 디버깅

from components.hitbox_component import HitboxComponent
from entities.weapons import BaseballBat 를 사용하여 적용 
tests\total\system\test_baseball_bat_integration.py 참고
