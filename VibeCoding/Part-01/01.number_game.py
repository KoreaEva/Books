import random


def number_guessing_game() -> None:
	answer = random.randint(1, 100)
	attempts = 0

	print("1부터 100 사이 숫자 맞추기 게임!")
	print("숫자를 입력해 주세요.")

	while True:
		user_input = input("입력: ").strip()

		if not user_input.isdigit():
			print("숫자만 입력해 주세요.")
			continue

		guess = int(user_input)
		if guess < 1 or guess > 100:
			print("1~100 사이의 숫자를 입력해 주세요.")
			continue

		attempts += 1

		if guess < answer:
			print("정답보다 작아요. 더 큰 숫자를 입력해 보세요!")
		elif guess > answer:
			print("정답보다 커요. 더 작은 숫자를 입력해 보세요!")
		else:
			print(f"정답입니다! {attempts}번 만에 맞췄어요.")
			break


if __name__ == "__main__":
	number_guessing_game()
