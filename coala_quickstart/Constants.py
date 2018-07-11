IMPORTANT_BEAR_LIST = {
    'All': {'FilenameBear', 'InvalidLinkBear', 'LineCountBear'},
    'C': {'GNUIndentBear', 'CSecurityBear', 'ClangComplexityBear'},
    'C#': {'CPDBear', 'CSharpLintBear', 'SpaceConsistencyBear'},
    'C++': {'GNUIndentBear', 'CPDBear', 'CPPCheckBear', 'CPPCleanBear',
            'ClangComplexityBear'},
    'CMake': {'CMakeLintBear', 'SpaceConsistencyBear'},
    'CSS': {'CSSLintBear', 'SpaceConsistencyBear'},
    'JavaScript': {'JSHintBear', 'JSComplexityBear'},
    'Java': {'JavaPMD', 'CheckstyleBear'},
    'Python': {'PycodestyleBear'}}

# This includes the bears from IMPORTANT_BEAR_LIST
GREEN_MODE_COMPATIBLE_BEAR_LIST = {}

ALL_CAPABILITIES = {
    'Code Simplification',
    'Commented Code',
    'Complexity',
    'Documentation',
    'Duplication',
    'Formatting',
    'Grammar',
    'Memory Leak',
    'Missing Import',
    'Redundancy',
    'Security',
    'Smell',
    'Spelling',
    'Syntax',
    'Undefined Element',
    'Unreachable Code',
    'Unused Code',
    'Variable Misuse'
}

DEFAULT_CAPABILTIES = {
    'Syntax',
    'Formatting',
    'Documentation',
    'Redundancy',
    'Spelling',
    'Smell',
    'Code Simplification',
    'Complexity',
}

HASHBANG_REGEX = '(^#!(.*))'
