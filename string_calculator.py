import unittest

DEFAULT_DELIMITER = ","

class NegativeValueException(Exception):
    def __init__(self, negative_values : list) -> None:
        print("Negatives not allowed")
        print(f"Negative values provided: {str(negative_values)[1:-1]}")
        super().__init__()

class ControlInfo():
    def __init__(self):
        self._delimiters = []
        self._control_code_length = 0

    @property
    def delimiters(self) -> list:
        return self._delimiters

    @property
    def control_code_length(self) -> int:
        return self._control_code_length

    def extract_delimiter(self, numbers: str) -> None:
        self._delimiters = []
        self._control_code_length = 0

        if numbers[0].isdigit() or numbers[0] == "-":
            self._delimiters.append(DEFAULT_DELIMITER)
        elif numbers[0] != "/" or numbers[1] != "/":
            raise Exception("Invalid Control Code")
        else:
            delimiter = ""
            self._control_code_length += 2
            for index, char in enumerate(numbers[2:]):
                if char.isdigit() or char == "-":
                    break
                if '\n' in numbers[2+index:3+index]:
                    self._control_code_length +=1
                    break
                if char == ",":
                    self._delimiters.append(delimiter)
                    delimiter = ""
                    self._control_code_length +=1
                else:
                    delimiter += char
                    self._control_code_length +=1
            self._delimiters.append(delimiter)

class StringCalculator():
    def __init__(self):
        self.control_info = ControlInfo()
        self._total = 0
        self._negative_values = []

    def add(self, numbers: str) -> int:
        self._total = 0
        self._negative_values = []

        if numbers:
            self.control_info.extract_delimiter(numbers)
            self._add_recursively(numbers[self.control_info.control_code_length:])

        if self._negative_values:
            raise NegativeValueException(self._negative_values)

        return self._total

    def _add_recursively(self, numbers: str) -> None:
        next_group = self._next_group(numbers)
        next_group_len = len(next_group)

        if not next_group:
            pass
        elif '\n' == next_group:
            self._add_recursively(numbers[2:])
        elif self._is_negative_val(next_group):
            self._negative_values.append(int(next_group))
            self._add_recursively(numbers[next_group_len:])
        elif next_group.isdigit():
            if int(next_group) <= 1000:
                self._total += int(next_group)
            self._add_recursively(numbers[next_group_len:])
        else:
            self._add_recursively(numbers[next_group_len:])

    def _is_negative_val(self, next_group: str) -> bool:
        is_negative = False
        if next_group[0] == '-' and next_group[1].isdigit():
            is_negative = True
        return is_negative

    def _next_group(self, numbers: str) -> str:
        next_group = ""
        if numbers:
            if numbers[0].isdigit():
                next_group = self._get_next_num(numbers)
            elif numbers[0] == "-":
                if not numbers[1].isdigit():
                    raise Exception("Invalid String Provided")
                next_group = "-" + self._get_next_num(numbers[1:])
            elif '\n' in numbers[:2]:
                next_group = numbers[:2]
            else:
                for delimiter in self.control_info.delimiters:
                    if delimiter == numbers[:len(delimiter)]:
                        next_group = delimiter
                        break
                if not next_group:
                    raise Exception("Invalid String Provided")

        return next_group

    def _get_next_num(self, numbers:str) -> str:
        multi_digit_value = ""
        for num in numbers:
            if not num.isdigit():
                break
            multi_digit_value += num

        return multi_digit_value

class StringCalculatorUnitTests(unittest.TestCase):
    def setUp(self):
        self.calculator = StringCalculator()
        self.control_info = ControlInfo()

    def test_empty_string_returns_zero(self):
        test_string = ""
        self.assertEqual(self.calculator.add(test_string), 0)

    def test_returns_zero(self):
        test_string = "0,0,0"
        self.assertEqual(self.calculator.add(test_string), 0)

    def test_sum_three_values(self):
        test_string = "1,2,5"
        self.assertEqual(self.calculator.add(test_string), 8)

    def test_sum_multiple_digit_values(self):
        test_string = "1,22,555"
        self.assertEqual(self.calculator.add(test_string), 578)

    def test_empty_input_returns_int_type(self):
        test_string = ""
        self.assertIsInstance(self.calculator.add(test_string), int)

    def test_non_empty_input_returns_int_type(self):
        test_string = "1,2,3"
        self.assertIsInstance(self.calculator.add(test_string), int)

    def test_new_line_is_ignored(self):
        test_string = "1\n,2,3"
        self.assertEqual(self.calculator.add(test_string), 6)

    def test_two_new_lines_are_ignored(self):
        test_string = "1\n,2\n,3"
        self.assertEqual(self.calculator.add(test_string), 6)

    def test_new_lines_are_ignored_with_multiple_digit_values(self):
        test_string = "1\n,20\n,300"
        self.assertEqual(self.calculator.add(test_string), 321)

    def test_invalid_control_code(self):
        test_string = "/1,2,3"
        self.assertRaises(Exception, self.control_info.extract_delimiter, test_string)

    def test_one_character_delimiter(self):
        test_string = "//@1@2@3"
        self.control_info.extract_delimiter(test_string)
        self.assertEqual(self.control_info.delimiters, ["@"])

    def test_two_character_delimiter(self):
        test_string = "//@#1@#2@#3"
        self.control_info.extract_delimiter(test_string)
        self.assertEqual(self.control_info.delimiters, ["@#"])
        self.assertEqual(self.calculator.add(test_string), 6)

    def test_two_character_delimiter_with_multiple_digit_values(self):
        test_string = "//@#1@#20@#300"
        self.control_info.extract_delimiter(test_string)
        self.assertEqual(self.control_info.delimiters, ["@#"])
        self.assertEqual(self.calculator.add(test_string), 321)

    def test_three_character_control_code(self):
        test_string = "//@1@2@3"
        self.control_info.extract_delimiter(test_string)
        self.assertEqual(self.control_info.control_code_length, 3)
        self.assertEqual(self.calculator.add(test_string), 6)

    def test_five_character_control_code(self):
        test_string = "//@#$1@#$2@#$3"
        self.control_info.extract_delimiter(test_string)
        self.assertEqual(self.control_info.control_code_length, 5)
        self.assertEqual(self.calculator.add(test_string), 6)

    def test_values_over_1000_not_added(self):
        test_string = "2,1001"
        self.assertEqual(self.calculator.add(test_string), 2)

    def test_two_delimiters(self):
        test_string = "//$,@\n1$2@3"
        self.control_info.extract_delimiter(test_string)
        self.assertEqual(self.control_info.delimiters, ["$", "@"])
        self.assertEqual(self.control_info.control_code_length, 6)
        self.assertEqual(self.calculator.add(test_string), 6)

    def test_two_delimiters_with_value_over_1000(self):
        test_string = "//$,@\n1001$2@3"
        self.control_info.extract_delimiter(test_string)
        self.assertEqual(self.control_info.delimiters, ["$", "@"])
        self.assertEqual(self.control_info.control_code_length, 6)
        self.assertEqual(self.calculator.add(test_string), 5)

    def test_three_delimiters(self):
        test_string = "//$,@,##\n1$2@3\n$4##5"
        self.control_info.extract_delimiter(test_string)
        self.assertEqual(self.control_info.delimiters, ["$", "@", "##"])
        self.assertEqual(self.control_info.control_code_length, 9)
        self.assertEqual(self.calculator.add(test_string), 15)

    def test_negative_value_throws_exception(self):
        test_string = "-1,-2"
        self.assertRaises(NegativeValueException, self.calculator.add, test_string)

    def test_positive_and_negative_values_throw_exception(self):
        test_string = "1,-20,3"
        self.assertRaises(NegativeValueException, self.calculator.add, test_string)

    def test_three_delimiters_with_negative_values(self):
        test_string = "//$,@,##\n1$-2@3\n$4##-50"
        self.assertRaises(NegativeValueException, self.calculator.add, test_string)

if __name__ == '__main__':
    unittest.main(verbosity=2)
