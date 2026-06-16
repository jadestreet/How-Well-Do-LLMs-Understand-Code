# abc123_b.py
# https://atcoder.jp/contests/abc123/tasks/abc123_b

# ★ RE:1
# in2.txt

# B - Five Dishes /
# 実行時間制限: 2 sec / メモリ制限: 1024 MB
# 配点: 200点

# 問題文
# AtCoder 料理店では、以下の 5つの料理が提供されています。ここで、「調理時間」は料理を注文してから客に届くまでの時間とします。
#     ABC 丼： 調理時間 A分
#     ARC カレー： 調理時間 B分
#     AGC パスタ： 調理時間 C分
#     APC ラーメン： 調理時間 D分
#     ATC ハンバーグ： 調理時間 E分

# また、この店には以下のような「注文のルール」があります。
#     注文は、10の倍数の時刻 (時刻 0,10,20,30,...) にしかできない。
#     一回の注文につき一つの料理しか注文できない。
#     ある料理を注文したら、それが届くまで別の注文ができない。ただし、料理が届いたちょうどの時刻には注文ができる。

# E869120 君は時刻 0に料理店に着きました。彼は 5 つの料理全てを注文します。最後の料理が届く最も早い時刻を求めてください。
# ただし、料理を注文する順番は自由であり、時刻 0に注文することも可能とであるとします。

# 制約
#     A,B,C,D,Eは 1 以上 123以下の整数

# 入力
# 入力は以下の形式で標準入力から与えられる。
# A
# B
# C
# D
# E

# 出力
# 最後の料理が届く最も早い時刻を整数で出力せよ。

# 入力例 1
# 29
# 20
# 7
# 35
# 120

# 出力例 1
# 215

# ABC 丼→ARC カレー→AGC パスタ→ATC ハンバーグ→APC ラーメン の順に注文することにすると、各料理の最も早い注文時刻・届く時刻は以下の通りになります。

#     時刻 0に ABC 丼を注文する。時刻 29に ABC 丼が届く。
#     時刻 30に ARC カレーを注文する。時刻 50に ARC カレーが届く。
#     時刻 50に AGC パスタを注文する。57に AGC パスタが届く。
#     時刻 60に ATC ハンバーグを注文する。時刻 180に ATC ハンバーグが届く。
#     時刻 180に APC ラーメンを注文する。時刻 215に APC ラーメンが届く。

# これより早く最後の料理が届くような方法は存在しません。

# 入力例 2
# 101
# 86
# 119
# 108
# 57

# 出力例 2
# 481

# AGC パスタ→ARC カレー→ATC ハンバーグ→APC ラーメン→ABC 丼の順に注文することにすると、各料理の最も早い注文時刻・届く時刻は以下の通りになります。

#     時刻 0に AGC パスタを注文する。時刻 119に AGC パスタが届く。
#     時刻 120に ARC カレーを注文する。時刻 206に ARC カレーが届く。
#     時刻 210に ATC ハンバーグを注文する。時刻 267に ATC ハンバーグが届く。
#     時刻 270に APC ラーメンを注文する。時刻 378に APC ラーメンが届く。
#     時刻 380に ABC 丼を注文する。時刻 481に ABC 丼が届く。

# これより早く最後の料理が届くような方法は存在しません。

# 入力例 3
# 123
# 123
# 123
# 123
# 123

# 出力例 3
# 643

# これが入力される最大のケースです。 


global FLAG_LOG
FLAG_LOG = False


def log(value):
    # FLAG_LOG = True
    # FLAG_LOG = False
    if FLAG_LOG:
        print(str(value))


def calculation(lines):
    # line = lines[0]
    # N = int(lines[0])
    # N, Q = list(map(int, lines[0].split()))
    # values = list(map(int, lines[1].split()))
    # values = list(map(int, lines[1].split()))
    values = list()
    for i in range(5):
        values.append(int(lines[i]))
    # valueses = list()
    # for i in range(Q):
    #     valueses.append(list(map(int, lines[i+1].split())))

    su = 0
    amaris = list()

    for value in values:
        amari = value % 10
        if amari > 0:
            amaris.append(10-amari)

    if amaris == []:
        result = sum(values)
    else:
        result = sum(values) + sum(amaris) - max(amaris)

    return [result]


# 引数を取得
def get_input_lines(lines_count):
    lines = list()
    for _ in range(lines_count):
        lines.append(input())
    return lines


# テストデータ
def get_testdata(pattern):
    if pattern == 1:
        lines_input = ['29', '20', '7', '35', '120']
        lines_export = [215]
    if pattern == 2:
        lines_input = ['101', '86', '119', '108', '57']
        lines_export = [481]
    if pattern == 3:
        lines_input = ['123', '123', '123', '123', '123']
        lines_export = [643]
    if pattern == -1:
        lines_input = ['10', '10', '10', '10', '10']
        lines_export = [50]
    return lines_input, lines_export


# 動作モード判別
def get_mode():
    import sys
    args = sys.argv
    global FLAG_LOG
    if len(args) == 1:
        mode = 0
        FLAG_LOG = False
    else:
        mode = int(args[1])
        FLAG_LOG = True
    return mode


# 主処理
def main():
    import time
    started = time.time()
    mode = get_mode()
    if mode == 0:
        lines_input = get_input_lines(5)
    else:
        lines_input, lines_export = get_testdata(mode)

    lines_result = calculation(lines_input)

    for line_result in lines_result:
        print(line_result)

    if FLAG_LOG:
        log(f'lines_input=[{lines_input}]')
        log(f'lines_export=[{lines_export}]')
        log(f'lines_result=[{lines_result}]')
        if lines_result == lines_export:
            log('OK')
        else:
            log('NG')
    finished = time.time()
    duration = finished - started
    log(f'duration=[{duration}]')


# 起動処理
if __name__ == '__main__':
    main()
