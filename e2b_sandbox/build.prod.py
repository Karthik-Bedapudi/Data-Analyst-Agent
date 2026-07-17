# build.prod.py
from dotenv import load_dotenv
from e2b import Template, default_build_logger
from template import template

load_dotenv()

if __name__ == '__main__':
    Template.build(
        template,
        'custom-packages',
        cpu_count=2,
        memory_mb=2048,
        on_build_logs=default_build_logger(),
    )