# Make edx a proper module to be imported
# Import tempdir fix when this module is accessed
try:
    from edx.utils import tempdir  # noqa: F401 - imported for side effects
except Exception as e:
    import sys
    print(f"Error importing edx.utils.tempdir: {e}", file=sys.stderr)
