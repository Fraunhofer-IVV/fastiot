from typing import List, Optional

from pydantic.main import BaseModel


class ModulePackageConfig(BaseModel):
    """
    Definition of modules via a package name and a list of modules inside the package. Modules, which are not specified
    in the list, but are in the package are ignored.
    """
    package_name: str
    """The package name of the modules"""
    module_names: List[str]
    """The module names as a list of strings"""
    cache_name: str = ''
    """
    The name to use as the cache. If empty, no cache is used for building. It will use the first given tag for building 
    to append it and also use the docker registry cache as a prefix. So you only need to specify the base name. 
    Example: mypackage-cache
    """
    extra_caches: List[str] = None
    """
    A list of extra caches used to speed up building. It is intended if you want to read from other caches or different 
    tags. Each extra cache must match a cache name extended by ':' followed by the tag for the cache. Per default no
    extra caches are used. You might find it useful to always include the cache name of the current module package 
    followed by tag latest to always use latest cache for feature branches.
    Examples: mypackage-cache:latest, sam-cache:latest, sam-cache:mybranch
    """

    def __post_init__(self):
        if self.extra_caches is None:
            self.extra_caches = []


class CustomModuleConfig(BaseModel):
    """
    Definition of a custom module. A custom module uses its own dockerfile instead of a predefined one.
    """
    module_name: str
    """Name of custom module"""
    workdir: str
    """The workdir defines the directory, where the dockerfile is executed. It is project root dir or a subdir of 
    project root dir in most case, but can be anywhere."""
    dockerfile_filename: str = 'Dockerfile'
    """The name of the dockerfile. You may specify it, if it lies in a subdir and not inside workdir."""
    manifest_filename: str = 'manifest.yaml'
    """The manifest.yaml is needed to be compatible with sam-compose. Please make sure to copy it to 
    '/opt/sam/manifest.yaml' inside the dockerimage. """
    do_use_debug_mode: bool = False
    """If true it will use a multi-stage build target 'debug' if mode debug is specified. This way, you can implement 
    custom functionality for debugging."""
    cache_name: str = ''
    """
    The cache name for the custom module. Works the same like cache name from module package config.
    """
    extra_caches: Optional[List[str]] = None
    """
    The extra caches to read from for the custom module. Works the same like extra caches from module package config.
    """

    def __post_init__(self):
        if self.extra_caches is None:
            self.extra_caches = []


class ProjectConfiguration(BaseModel):
    """ This class holds all variables reade from :file:`configure.py` in the project root directory. """

    project_root_dir: str
    project_namespace: str
    library_package: Optional[str]
    library_setup_py_dir: Optional[str] = None
    module_packages: Optional[List[ModulePackageConfig]] = None
    custom_modules: Optional[List[CustomModuleConfig]] = None
    deploy_configs: List[str]
    test_config: Optional[str]
    test_package: Optional[str]
    imports_for_test_config_environment_variables: Optional[List[str]] = None
    npm_test_dir: Optional[str] = None
