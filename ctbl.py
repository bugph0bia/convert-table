import os
import sys
import argparse
from argparse import RawTextHelpFormatter
import io
import csv
import re
import unicodedata


DESCRIPTION = """Planetext Table Comverter.

  Input/Output types:
    csv   : comma separated values.
    tsv   : tab separated values (like copied from spreadsheet)
    md    : markdown style table
    ascii : Ascii style table (similar to reST's grid style, but cell merge is not available)
"""


class Cell(str):
    """str with alignment"""
    LEFT = 'l'
    CENTER = 'c'
    RIGHT = 'r'

    def __new__(cls, text, align=LEFT):
        self = super().__new__(cls, text)
        self.align = align
        return self

    def __repr__(self):
        return f'{self.align}:{self}'

    def __len__(self):
        width = 0
        for char in self:
            width += 2 if unicodedata.east_asian_width(char) in 'FWA' else 1
        return width


def main():
    """main"""
    # コマンドライン引数処理
    parser = argparse.ArgumentParser(description=DESCRIPTION,
                                     formatter_class=RawTextHelpFormatter)
    parser.add_argument('-i', help='input type')
    parser.add_argument('-o', help='output type')
    args = parser.parse_args()

    itype = (args.i or '').lower()
    otype = (args.o or '').lower()

    # 入力
    with open(sys.stdin.fileno(), 'r', newline='') as f:
        lines = f.readlines()

    if itype == 'csv':
        data = input_csv(lines)
    elif itype == 'tsv':
        data = input_csv(lines, delimiter='\t')
    elif itype == 'md':
        data = input_md(lines)
    elif itype == 'ascii':
        data = input_ascii(lines)
    else:
        print('-i: invalid argments')
        sys.exit()

    # 出力
    if otype == 'csv':
        text = output_csv(data)
    elif otype == 'tsv':
        text = output_csv(data, delimiter='\t')
    elif otype == 'md':
        text = output_md(data)
    elif otype == 'ascii':
        text = output_ascii(data)
    else:
        print('-o: invalid argments')
        sys.exit()
    with open(sys.stdout.fileno(), 'w', newline='') as f:
        f.write(text)


def input_csv(lines, delimiter=','):
    text = ''.join(lines)
    with io.StringIO(newline='') as stream:
        stream.write(text)
        stream.seek(0)
        reader = csv.reader(stream, delimiter=delimiter)
        data = [[Cell(cell) for cell in row] for row in reader]
    return data


def input_md(lines):
    def convbr(t):
        """br タグを改行に変換"""
        return Cell(t.replace('</br>', os.linesep).replace('<br/>', os.linesep))

    aligns = []
    data = []
    for i, line in enumerate(lines):
        line = line.strip()

        # 罫線行
        if i == 1 and re.match(r'^\|( ?:?-+:? ?\|)+$', line):
            # アライメントを保存
            for text in line[1:-1].split('|'):
                text = text.strip()
                left = text.startswith(':')
                right = text.endswith(':')
                if left and right:
                    aligns.append(Cell.CENTER)
                elif right:
                    aligns.append(Cell.RIGHT)
                else:
                    aligns.append(Cell.LEFT)
        # データ行
        else:
            # Markdown 書式でなければ終了
            if not line.startswith('|') or not line.endswith('|'):
                break

            d = [convbr(text.strip()) for text in line[1:-1].split('|')]
            data.append(d)

    # アライメントを設定
    for i, a in enumerate(aligns):
        for row in data:
            if i < len(row):
                row[i].align = a

    return data


def input_ascii(lines):

    def compress():
        """tmpdata を圧縮して data へ連結"""
        nonlocal tmpdata, data

        cmprow = []
        for tmprow in tmpdata:
            if cmprow:
                for i, (src, dst) in enumerate(zip(tmprow, cmprow)):
                    # 文字列のみ上のセルへ連結
                    # アラインは上のセルを採用
                    cmprow[i] = Cell(dst + '\n' + src, align=dst.align)
            else:
                cmprow = tmprow
        if cmprow:
            cmprow = [Cell(c.strip(), align=c.align) for c in cmprow]
            data.append(cmprow)
        tmpdata = []

    data = []
    tmpdata = []
    for i, line in enumerate(lines):
        line = line.strip()

        # 罫線行
        if re.match(r'[-+]+', line):
            # ここまでのデータを圧縮して格納
            compress()

        # データ行
        else:
            # ascii 書式でなければ終了
            if not line.startswith('|') or not line.endswith('|'):
                break

            d = []
            for text in line[1:-1].split('|'):
                lsp = text.startswith(' ')
                rsp = text.endswith(' ')
                if lsp and rsp:
                    align = Cell.CENTER
                elif lsp:
                    align = Cell.RIGHT
                else:
                    align = Cell.LEFT
                d.append(Cell(text.strip(), align=align))
            tmpdata.append(d)

    # 最終データを圧縮して格納
    compress()
    return data


def output_csv(data, delimiter=','):
    with io.StringIO(newline='') as stream:
        writer = csv.writer(stream, delimiter=delimiter)
        writer.writerows(data)
        return stream.getvalue()


def output_md(data):

    def convbr(t):
        """改行を br タグに変換"""
        return Cell(t.replace('\r\n', '<br/>').replace('\r', '<br/>').replace('\r', '<br/>'), align=t.align)

    # 改行を br タグに変換
    data = [[convbr(cell) for cell in row] for row in data]
    # 各列の必要幅を取得
    collens = column_lengths(data)

    def ruleline():
        """罫線行"""
        nonlocal collens, data
        rline = '|'
        for collen, cell in zip(collens, data[0]):
            rcell = '-' * (collen - 2)
            if cell.align == Cell.LEFT:
                rcell = ':' + rcell + '-'
            elif cell.align == Cell.CENTER:
                rcell = ':' + rcell + ':'
            else:
                rcell = '-' + rcell + ':'
            rline += rcell + '|'
        return rline + os.linesep

    def dataline(row):
        """データ行"""
        nonlocal collens
        dline = '|'
        for collen, cell in zip(collens, row):
            # 前後に余白を付与
            # ※ column_lengths でその分余分に幅をカウントしてある
            collen -= len(cell)
            lsp = ' '
            rsp = ' ' * (collen - 1)
            dline += lsp + cell + rsp + '|'
        return dline + os.linesep

    # 文字列化
    text = dataline(data[0])
    text += ruleline()
    for row in data[1:]:
        text += dataline(row)
    return text


def output_ascii(data):
    # セル内改行を複数行データに分割
    continues = []
    new_data = []
    for row in data:
        # 先に行の分割数を計算
        cnt = max([len(cell.splitlines()) for cell in row])

        new_rows = [[] for _ in range(cnt)]  # [[]] * cnt にしてしまうと内側の [] がすべて同じオブジェクトになるので注意
        for cell in row:
            # セルを改行で分割
            new_cells = cell.splitlines()
            # 行の分割数に満たない場合は空文字で埋める
            new_cells.extend([''] * (cnt - len(new_cells)))
            # Cellオブジェクト化
            new_cells = [Cell(nc, align=cell.align) for nc in new_cells]
            # 分割後の新しい行データを作成
            for i in range(cnt):
                new_rows[i].append(new_cells[i])
        # 新しいデータに格納
        new_data.extend(new_rows)
        # 分割された2行目以降は連結フラグを立てる
        continues.append(False)
        continues.extend([True] * (cnt - 1))
    data = new_data

    # 各列の必要幅を取得
    collens = column_lengths(data)

    def ruleline():
        """罫線行"""
        nonlocal collens, data
        rline = '+'
        for collen, cell in zip(collens, data[0]):
            rcell = '-' * collen
            rline += rcell + '+'
        return rline + os.linesep

    def dataline(row):
        """データ行"""
        nonlocal collens
        dline = '|'
        for collen, cell in zip(collens, row):
            # 前後に余白を付与
            # ※ column_lengths でその分余分に幅をカウントしてある
            collen -= len(cell)
            if cell.align == Cell.CENTER:
                lsp = ' ' * (collen // 2)
                rsp = ' ' * (collen // 2 + collen % 2)
            elif cell.align == Cell.RIGHT:
                lsp = ' ' * (collen - 1)
                rsp = ' '
            else:
                lsp = ' '
                rsp = ' ' * (collen - 1)
            dline += lsp + cell + rsp + '|'
        return dline + os.linesep

    # 文字列化
    text = ''
    for row, is_continue in zip(data, continues):
        if not is_continue:
            text += ruleline()
        text += dataline(row)
    text += ruleline()
    return text


def column_lengths(data):
    """各列の必要幅を計算"""
    collens = []
    for row in data:
        if not collens:
            collens = [0] * len(row)
        for i, (cell, collen) in enumerate(zip(row, collens)):
            # 文字幅 + 前後の空白SP1文字 の幅をする
            # ※最低でも3文字幅とする
            collens[i] = max(len(cell) + 2, collen, 3)
    return collens


if __name__ == '__main__':
    main()
