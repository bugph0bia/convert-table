import unittest
import os

from ctbl import Cell
from ctbl import input_csv, input_md, input_ascii
from ctbl import output_csv, output_md, output_ascii


class TestInput(unittest.TestCase):
    def test_input_csv(self):
        lines = [
            'aaa,bbb,ccc',
            '"aaa","bbb","ccc"',
            'aa\ta,"bb\nb",ccc',
        ]
        lines = [line + os.linesep for line in lines]

        data = input_csv(lines, delimiter=',')

        self.assertEqual(data[0][0], 'aaa')
        self.assertEqual(data[0][1], 'bbb')
        self.assertEqual(data[0][2], 'ccc')
        self.assertEqual(data[1][0], 'aaa')
        self.assertEqual(data[1][1], 'bbb')
        self.assertEqual(data[1][2], 'ccc')
        self.assertEqual(data[2][0], 'aa\ta')
        self.assertEqual(data[2][1], 'bb\nb')
        self.assertEqual(data[2][2], 'ccc')
        self.assertEqual(data[0][0].align, Cell.LEFT)
        self.assertEqual(data[0][1].align, Cell.LEFT)
        self.assertEqual(data[0][2].align, Cell.LEFT)
        self.assertEqual(data[1][0].align, Cell.LEFT)
        self.assertEqual(data[1][1].align, Cell.LEFT)
        self.assertEqual(data[1][2].align, Cell.LEFT)
        self.assertEqual(data[2][0].align, Cell.LEFT)
        self.assertEqual(data[2][1].align, Cell.LEFT)
        self.assertEqual(data[2][2].align, Cell.LEFT)

    def test_input_tsv(self):
        lines = [
            'aaa\tbbb\tccc',
            '"aaa"\t"bbb"\t"ccc"',
            'aa,a\t"bb\nb"\tccc',
        ]
        lines = [line + os.linesep for line in lines]

        data = input_csv(lines, delimiter='\t')

        self.assertEqual(data[0][0], 'aaa')
        self.assertEqual(data[0][1], 'bbb')
        self.assertEqual(data[0][2], 'ccc')
        self.assertEqual(data[1][0], 'aaa')
        self.assertEqual(data[1][1], 'bbb')
        self.assertEqual(data[1][2], 'ccc')
        self.assertEqual(data[2][0], 'aa,a')
        self.assertEqual(data[2][1], 'bb\nb')
        self.assertEqual(data[2][2], 'ccc')
        self.assertEqual(data[0][0].align, Cell.LEFT)
        self.assertEqual(data[0][1].align, Cell.LEFT)
        self.assertEqual(data[0][2].align, Cell.LEFT)
        self.assertEqual(data[1][0].align, Cell.LEFT)
        self.assertEqual(data[1][1].align, Cell.LEFT)
        self.assertEqual(data[1][2].align, Cell.LEFT)
        self.assertEqual(data[2][0].align, Cell.LEFT)
        self.assertEqual(data[2][1].align, Cell.LEFT)
        self.assertEqual(data[2][2].align, Cell.LEFT)

    def test_input_md(self):
        lines = [
            '| aaa | bbb | ccc | ddd |',
            '|:----|:---:|----:| --- |',
            '| aaa | bbb | ccc | ddd |',
            '| aa\ta | bb<br/>b | cc</br>c | ddd |',
        ]
        lines = [line + os.linesep for line in lines]

        data = input_md(lines)

        self.assertEqual(data[0][0], 'aaa')
        self.assertEqual(data[0][1], 'bbb')
        self.assertEqual(data[0][2], 'ccc')
        self.assertEqual(data[0][3], 'ddd')
        self.assertEqual(data[1][0], 'aaa')
        self.assertEqual(data[1][1], 'bbb')
        self.assertEqual(data[1][2], 'ccc')
        self.assertEqual(data[1][3], 'ddd')
        self.assertEqual(data[2][0], 'aa\ta')
        self.assertEqual(data[2][1], 'bb\nb')
        self.assertEqual(data[2][2], 'cc\nc')
        self.assertEqual(data[2][3], 'ddd')
        self.assertEqual(data[0][0].align, Cell.LEFT)
        self.assertEqual(data[0][1].align, Cell.CENTER)
        self.assertEqual(data[0][2].align, Cell.RIGHT)
        self.assertEqual(data[0][3].align, Cell.LEFT)
        self.assertEqual(data[1][0].align, Cell.LEFT)
        self.assertEqual(data[1][1].align, Cell.CENTER)
        self.assertEqual(data[1][2].align, Cell.RIGHT)
        self.assertEqual(data[1][3].align, Cell.LEFT)
        self.assertEqual(data[2][0].align, Cell.LEFT)
        self.assertEqual(data[2][1].align, Cell.CENTER)
        self.assertEqual(data[2][2].align, Cell.RIGHT)
        self.assertEqual(data[2][3].align, Cell.LEFT)

    def test_input_ascii(self):
        lines = [
            '+-----+-----+-----+-----+',
            '| aaa | bbb | ccc | ddd |',
            '+-----+-----+-----+-----+',
            '|aaa  | bbb |  ccc|ddddd|',
            '+-----+-----+-----+-----+',
            '| aaa |bbb  | ccc |     |',
            '| aaa | bbb |     |     |',
            '| aaa |  bbb| ccc |     |',
            '+-----+-----+-----+-----+',
        ]
        lines = [line + os.linesep for line in lines]

        data = input_ascii(lines)

        self.assertEqual(data[0][0], 'aaa')
        self.assertEqual(data[0][1], 'bbb')
        self.assertEqual(data[0][2], 'ccc')
        self.assertEqual(data[0][3], 'ddd')
        self.assertEqual(data[1][0], 'aaa')
        self.assertEqual(data[1][1], 'bbb')
        self.assertEqual(data[1][2], 'ccc')
        self.assertEqual(data[1][3], 'ddddd')
        self.assertEqual(data[2][0], 'aaa\naaa\naaa')
        self.assertEqual(data[2][1], 'bbb\nbbb\nbbb')
        self.assertEqual(data[2][2], 'ccc\n\nccc')
        self.assertEqual(data[2][3], '')
        self.assertEqual(data[0][0].align, Cell.CENTER)
        self.assertEqual(data[0][1].align, Cell.CENTER)
        self.assertEqual(data[0][2].align, Cell.CENTER)
        self.assertEqual(data[0][3].align, Cell.CENTER)
        self.assertEqual(data[1][0].align, Cell.LEFT)
        self.assertEqual(data[1][1].align, Cell.CENTER)
        self.assertEqual(data[1][2].align, Cell.RIGHT)
        self.assertEqual(data[1][3].align, Cell.LEFT)
        self.assertEqual(data[2][0].align, Cell.CENTER)
        self.assertEqual(data[2][1].align, Cell.LEFT)
        self.assertEqual(data[2][2].align, Cell.CENTER)
        self.assertEqual(data[2][3].align, Cell.CENTER)


class TestOutput(unittest.TestCase):
    def test_output_csv(self):
        data = [
            [
                Cell('aaa'),
                Cell('bbb'),
                Cell('ccc'),
            ],
            [
                Cell('aaa', Cell.LEFT),
                Cell('bbb', Cell.CENTER),
                Cell('ccc', Cell.RIGHT),
            ],
            [
                Cell('aa\ta'),
                Cell('bb\nb'),
                Cell('ccc'),
            ],
        ]

        text = output_csv(data, delimiter=',')

        self.assertEqual(
            text,
            (
                f'aaa,bbb,ccc{os.linesep}'
                f'aaa,bbb,ccc{os.linesep}'
                f'aa\ta,"bb\nb",ccc{os.linesep}'
            )
        )

    def test_output_tsv(self):
        data = [
            [
                Cell('aaa'),
                Cell('bbb'),
                Cell('ccc'),
            ],
            [
                Cell('aaa', Cell.LEFT),
                Cell('bbb', Cell.CENTER),
                Cell('ccc', Cell.RIGHT),
            ],
            [
                Cell('aa,a'),
                Cell('bb\nb'),
                Cell('ccc'),
            ],
        ]
        text = output_csv(data, delimiter='\t')
        self.assertEqual(
            text,
            (
                f'aaa\tbbb\tccc{os.linesep}'
                f'aaa\tbbb\tccc{os.linesep}'
                f'aa,a\t"bb\nb"\tccc{os.linesep}'
            )
        )

    def test_output_md(self):
        data = [
            [
                Cell('a', Cell.LEFT),
                Cell('bbb', Cell.CENTER),
                Cell('ccc', Cell.RIGHT),
            ],
            [
                Cell('', Cell.CENTER),
                Cell('bbb', Cell.RIGHT),
                Cell('あいうえお'),
            ],
            [
                Cell('a'),
                Cell('bb\nb'),
                Cell('cccccc'),
            ],
        ]
        text = output_md(data)
        self.assertEqual(
            text,
            (
                f'| a | bbb      | ccc        |{os.linesep}'
                f'|:--|:--------:|-----------:|{os.linesep}'
                f'|   | bbb      | あいうえお |{os.linesep}'
                f'| a | bb<br/>b | cccccc     |{os.linesep}'
            )
        )

    def test_output_ascii(self):
        data = [
            [
                Cell('a', Cell.LEFT),
                Cell('bbb', Cell.CENTER),
                Cell('ccc', Cell.RIGHT),
            ],
            [
                Cell('', Cell.CENTER),
                Cell('bbb', Cell.RIGHT),
                Cell('あいうえお'),
            ],
            [
                Cell('a'),
                Cell('bb\nbbbbb'),
                Cell('cccccc'),
            ],
        ]
        text = output_ascii(data)
        self.assertEqual(
            text,
            (
                f'+---+-------+------------+{os.linesep}'
                f'| a |  bbb  |        ccc |{os.linesep}'
                f'+---+-------+------------+{os.linesep}'
                f'|   |   bbb | あいうえお |{os.linesep}'
                f'+---+-------+------------+{os.linesep}'
                f'| a | bb    | cccccc     |{os.linesep}'
                f'|   | bbbbb |            |{os.linesep}'
                f'+---+-------+------------+{os.linesep}'
            )
        )

