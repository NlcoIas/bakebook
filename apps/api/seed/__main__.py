"""Allow running seed as: python -m seed.seed"""

from seed.seed import main

if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
