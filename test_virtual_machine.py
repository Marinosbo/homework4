import unittest
import subprocess
import os
import csv


class TestVirtualMachine(unittest.TestCase):
    def setUp(self):   #подготовки тестовой среды
        # Создаем тестовые файлы
        self.asm_file = "test_vector_sgn.asm"
        self.binary_file = "test_vector_sgn.bin"
        self.log_file = "test_log.csv"
        self.result_file = "test_memory_result.csv"
        self.input_memory_file = "test_memory_input.csv"
        self.expected_output_file = "expected_memory_output.csv"

        asm_code = """
        LOAD_CONST 0
        WRITE_MEM 20
        loop:
        READ_MEM 20
        READ_MEM 0
        SGN 0
        WRITE_MEM 10
        READ_MEM 20
        LOAD_CONST 1
        ADD
        WRITE_MEM 20
        READ_MEM 20
        LOAD_CONST 6
        SUB
        JZ end
        JMP loop
        end:
        HALT
        """
        with open(self.asm_file, "w") as asm:
            asm.write(asm_code.strip())

        # Входные данные в память (вектор: [3, -2, 0, 7, -5, 4])
        input_memory = [
            {"address": 0, "value": 3},
            {"address": 1, "value": -2},
            {"address": 2, "value": 0},
            {"address": 3, "value": 7},
            {"address": 4, "value": -5},
            {"address": 5, "value": 4},
        ]
        with open(self.input_memory_file, "w") as mem_file:
            writer = csv.DictWriter(mem_file, fieldnames=["address", "value"])
            writer.writeheader()
            writer.writerows(input_memory)

        # Ожидаемый результат
        expected_output = [
            {"address": 10, "value": 1},
            {"address": 11, "value": -1},
            {"address": 12, "value": 0},
            {"address": 13, "value": 1},
            {"address": 14, "value": -1},
            {"address": 15, "value": 1},
        ]
        with open(self.expected_output_file, "w") as exp_file:
            writer = csv.DictWriter(exp_file, fieldnames=["address", "value"])
            writer.writeheader()
            writer.writerows(expected_output)

    def tearDown(self):
        # Удаляем временные файлы после тестов
        for file in [
            self.asm_file,
            self.binary_file,
            self.log_file,
            self.result_file,
            self.input_memory_file,
            self.expected_output_file,
        ]:
            if os.path.exists(file):
                os.remove(file)

    def test_assemble(self):
        # Проверяем, что ассемблер создает бинарный файл без ошибок
        result = subprocess.run(
            ["python", "script.py", "assemble", self.asm_file, self.binary_file, self.log_file],
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertTrue(os.path.exists(self.binary_file))

        def test_interpreter(self):
            # Сначала запускаем ассемблер
            assemble_result = subprocess.run(
                ["python", "script.py", "assemble", self.asm_file, self.binary_file, self.log_file],
                capture_output=True,
                text=True,
            )
            self.assertEqual(assemble_result.returncode, 0, msg=assemble_result.stderr)
            self.assertTrue(os.path.exists(self.binary_file), msg="Binary file was not created.")

            # Теперь запускаем интерпретатор
            interpret_result = subprocess.run(
                [
                    "python",
                    "script.py",
                    "interpret",
                    self.binary_file,
                    self.result_file,
                    self.input_memory_file,
                ],
                capture_output=True,
                text=True,
            )
            self.assertEqual(interpret_result.returncode, 0, msg=interpret_result.stderr)

            # Сравниваем результат интерпретации
            with open(self.result_file, "r") as res_file, open(self.expected_output_file, "r") as exp_file:
                result_data = list(csv.DictReader(res_file))
                expected_data = list(csv.DictReader(exp_file))
                self.assertEqual(result_data, expected_data)


def test_full_cycle(self):
        # Полный цикл: ассемблирование -> интерпретация -> проверка результата
        assemble_result = subprocess.run(
            ["python", "script.py", "assemble", self.asm_file, self.binary_file, self.log_file],
            capture_output=True,
            text=True,
        )
        self.assertEqual(assemble_result.returncode, 0, msg=assemble_result.stderr)

        interpret_result = subprocess.run(
            [
                "python",
                "script.py",
                "interpret",
                self.binary_file,
                self.result_file,
                self.input_memory_file,
            ],
            capture_output=True,
            text=True,
        )
        self.assertEqual(interpret_result.returncode, 0, msg=interpret_result.stderr)

        # Сравниваем результат
        with open(self.result_file, "r") as res_file, open(self.expected_output_file, "r") as exp_file:
            result_data = list(csv.DictReader(res_file))
            expected_data = list(csv.DictReader(exp_file))
            self.assertEqual(result_data, expected_data)


if __name__ == "__main__":
    unittest.main()
