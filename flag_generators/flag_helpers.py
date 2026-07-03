import secrets
import string
import re
from typing import Set, List

class FlagUtils:
    """
    Utility class for flag generation and validation.
    Refined for better entropy, performance, and collision avoidance.
    """
    
    # Pre-compile the regex once to avoid overhead during repeated validation
    _REAL_FLAG_PATTERN = re.compile(r"^CCRI-[A-Z]{4}-\d{4}$")
    
    # Tracking used flags to prevent duplicates within a generation session
    _used_flags: Set[str] = set()

    @classmethod
    def generate_real_flag(cls) -> str:
        """
        Generate a valid CCRI flag: CCRI-ABCD-1234
        Uses 'secrets' for cryptographically strong random choices.
        """
        while True:
            letters = ''.join(secrets.choice(string.ascii_uppercase) for _ in range(4))
            digits = ''.join(secrets.choice(string.digits) for _ in range(4))
            flag = f"CCRI-{letters}-{digits}"
            
            if flag not in cls._used_flags:
                cls._used_flags.add(flag)
                return flag

    @classmethod
    def generate_fake_flag(cls) -> str:
        """
        Generate an invalid flag in one of two strict fake formats.
        Ensures the flag never starts with CCRI- and is unique.
        """
        while True:
            letters1 = ''.join(secrets.choice(string.ascii_uppercase) for _ in range(4))
            letters2 = ''.join(secrets.choice(string.ascii_uppercase) for _ in range(4))
            digits = ''.join(secrets.choice(string.digits) for _ in range(4))
            
            # 50/50 split on the format
            if secrets.choice([True, False]):
                fake = f"{letters1}-{letters2}-{digits}"
            else:
                fake = f"{letters1}-{digits}-{letters2}"

            # Ensure we don't accidentally match the real prefix
            if not fake.startswith("CCRI") and fake not in cls._used_flags:
                cls._used_flags.add(fake)
                return fake

    @classmethod
    def generate_batch(cls, count: int, is_real: bool = False) -> List[str]:
        """Utility to generate a batch of flags without duplicates."""
        return [cls.generate_real_flag() if is_real else cls.generate_fake_flag() for _ in range(count)]

    @classmethod
    def validate_flag_format(cls, flag: str) -> bool:
        """
        Validate flag format: CCRI-XXXX-1234
        """
        return bool(cls._REAL_FLAG_PATTERN.match(flag))

    @classmethod
    def clear_cache(cls):
        """Reset the used_flags cache."""
        cls._used_flags.clear()