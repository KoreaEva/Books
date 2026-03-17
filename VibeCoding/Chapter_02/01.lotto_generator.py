import random

def generate_ticket(seed=None):
    """
    로또 번호를 생성하는 함수
    
    Args:
        seed (int, optional): 난수 생성을 위한 시드값. None이면 무작위.
    
    Returns:
        list: 1-45 사이의 중복 없는 6개 번호를 오름차순으로 정렬한 리스트
    """
    if seed is not None:
        random.seed(seed)
    
    # 1부터 45까지의 숫자 중에서 중복 없이 6개 선택
    numbers = random.sample(range(1, 46), 6)
    
    # 오름차순으로 정렬
    return sorted(numbers)

def main():
    """
    메인 함수: 사용자 입력을 받아 로또 번호를 생성하고 출력
    """
    print("=== 로또 번호 생성기 ===")
    
    # 기본값 설정
    num_games = 1
    base_seed = None
    
    try:
        # 게임 수 입력받기
        games_input = input("생성할 게임 수를 입력하세요 (기본값: 1): ").strip()
        if games_input:
            num_games = int(games_input)
            if num_games <= 0:
                raise ValueError("게임 수는 양수여야 합니다.")
        
        # 시드값 입력받기
        seed_input = input("시드값을 입력하세요 (없으면 Enter로 무작위): ").strip()
        if seed_input:
            base_seed = int(seed_input)
    
    except ValueError as e:
        print(f"잘못된 입력입니다: {e}")
        print("기본값으로 설정합니다. (게임 수: 1, 시드: 무작위)")
        num_games = 1
        base_seed = None
    
    print(f"\n=== {num_games}게임 로또 번호 ===")
    
    # 로또 번호 생성 및 출력
    for i in range(1, num_games + 1):
        if base_seed is not None:
            # 여러 게임일 경우 base_seed + (i-1)로 시드를 다르게 설정
            current_seed = base_seed + (i - 1)
            ticket = generate_ticket(current_seed)
            print(f"게임 {i}: {ticket} (시드: {current_seed})")
        else:
            # 시드가 없으면 무작위
            ticket = generate_ticket()
            print(f"게임 {i}: {ticket}")
    
    print("\n행운을 빕니다! 🍀")

if __name__ == "__main__":
    main()