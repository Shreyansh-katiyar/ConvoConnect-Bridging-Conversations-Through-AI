def is_smart_city_possible(tower_heights):
    N = len(tower_heights)
    if N % 2 != 0:
        return False
    M = N // 2
    left_half = sorted(tower_heights[:M])
    right_half = sorted(tower_heights[M:])
    return left_half == right_half


def main():
    T = int(input())
    results = []

    for _ in range(T):
        N = int(input())
        tower_heights = list(map(int, input().split()))

        if is_smart_city_possible(tower_heights):
            results.append("YES")
        else:
            results.append("NO")

    for result in results:
        print(result)


if __name__ == "__main__":
    main()