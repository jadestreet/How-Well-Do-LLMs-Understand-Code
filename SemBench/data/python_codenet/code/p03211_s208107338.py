# abc114_b.py
# https://atcoder.jp/contests/abc114/tasks/abc114_b

# B - 754 /
# 実行時間制限: 2 sec / メモリ制限: 1024 MB
# 配点 : 200点

# 問題文
# 数字 1, 2, ..., 9 からなる文字列 S があります。 
# ダックスフンドのルンルンは、S から連続する 3 個の数字を取り出し、 1 つの整数 Xとしてご主人様の元に持っていきます。
# （数字の順番を変えることはできません。）
# ご主人様が大好きな数は 753で、これに近い数ほど好きです。 X と 753の差（の絶対値）は最小でいくつになるでしょうか？

# 制約
#     Sは長さ 4 以上 10以下の文字列である。
#     Sの各文字は 1, 2, ..., 9 のいずれかである。

# 入力
# 入力は以下の形式で標準入力から与えられる。
# S

# 出力
# Xと 753の差としてありうる最小値を出力せよ。

# 入力例 1
# 1234567876

# 出力例 1
# 34

# 7文字目から 9 文字目までを取り出すと X=787 となり、これと 753 との差は 787−753=34 です。
# Xをどこから取り出しても、差をより小さくすることはできません。
# なお、数字の順番を変えることはできません。例えば、567 を取り出して 765 に並び変えてはいけません。
# また、Sから連続していない 3 文字を取り出すこともできません。
# 例えば、7 文字目の 7、9 文字目の 7 と 10文字目の 6 を取り出して 776 としてはいけません。

# 入力例 2
# 35753

# 出力例 2
# 0

# 753 そのものを取り出すことができる場合、答えは 0です。

# 入力例 3
# 1111111111

# 出力例 3
# 642

# どこから 3文字を取り出しても X=111 となり、差は 753−111=642 です。


def calculation(lines):
    X = lines[0]
    # X = int(lines[0])
    # N, M = list(map(int, lines[0].split()))

    dif = None

    for i in range(len(X)-2):
        tmp = abs(int(X[i:i+3]) - 753)
        # print(f'tmp=[{tmp}]')
        # print(f'dif=[{dif}]')
        if dif is None:
            dif = tmp
        elif dif > tmp:
            dif = tmp

    return [dif]


# 引数を取得
def get_input_lines(lines_count):
    lines = list()
    for _ in range(lines_count):
        lines.append(input())
    return lines


# テストデータ
def get_testdata(pattern):
    if pattern == 1:
        lines_input = ['1234567876']
        lines_export = [34]
    if pattern == 2:
        lines_input = ['35753']
        lines_export = [0]
    if pattern == 3:
        lines_input = ['1111111111']
        lines_export = [642]
    return lines_input, lines_export


# 動作モード判別
def get_mode():
    import sys
    args = sys.argv
    if len(args) == 1:
        mode = 0
    else:
        mode = int(args[1])
    return mode


# 主処理
def main():
    import time
    started = time.time()
    mode = get_mode()
    if mode == 0:
        lines_input = get_input_lines(1)
    else:
        lines_input, lines_export = get_testdata(mode)

    lines_result = calculation(lines_input)

    for line_result in lines_result:
        print(line_result)

    # if mode > 0:
    #     print(f'lines_input=[{lines_input}]')
    #     print(f'lines_export=[{lines_export}]')
    #     print(f'lines_result=[{lines_result}]')
    #     if lines_result == lines_export:
    #         print('OK')
    #     else:
    #         print('NG')
    # finished = time.time()
    # duration = finished - started
    # print(f'duration=[{duration}]')


# 起動処理
if __name__ == '__main__':
    main()
