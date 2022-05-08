from string import ascii_lowercase as en, ascii_uppercase as EN, digits
from random import choice, shuffle, sample


class PasswordError(Exception):
    pass


class LengthError(PasswordError):
    pass


class LetterError(PasswordError):
    pass


class DigitError(PasswordError):
    pass


def criteria(password):
    """Password criteria"""
    if len(password) < 8:
        raise LengthError('The password contains less than 8 characters')
    if password.lower() == password or password.upper() == password:
        raise LetterError('The password must contain mixed case characters')
    is_num_ok = False
    is_alpha_ok = False
    for symbol in password:
        if symbol.isdigit():
            is_num_ok = True
        elif symbol.isalpha():
            is_alpha_ok = True
        if is_num_ok and is_alpha_ok:
            break
    if not is_num_ok or not is_alpha_ok:
        raise DigitError('The password does not contain a digit')
    return 'ok'


def check_password(password):
    """Checks if the password matches the criteria."""
    try:
        return criteria(password)
    except DigitError as err:
        return err.args[0]
    except LengthError as err:
        return err.args[0]
    except LetterError as err:
        return err.args[0]


def generate_password(m):
    """Generate random password that matches the criteria"""
    assert m >= 3
    valid_EN = set(EN) - {'I', 'O'}
    p_EN = choice(list(valid_EN))
    rest_EN = list(valid_EN - {p_EN})
    valid_en = set(en) - {'l', 'o'}
    p_en = choice(list(valid_en))
    rest_en = list(valid_en - {p_en})
    valid_digits = set(digits) - {'0', '1'}
    p_digit = choice(list(valid_digits))
    rest_digits = list(valid_digits - {p_digit})
    all_rest_valid = rest_EN + rest_en + rest_digits
    password = sample(all_rest_valid, m - 3) + [p_EN, p_en, p_digit]
    shuffle(password)
    return ''.join(password)


if __name__ == '__main__':
    pass