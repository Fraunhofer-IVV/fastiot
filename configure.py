from fastiot.cli import find_modules

extensions = ['fastiot_ivv_tools.extension']

project_namespace = 'fastiot'

library_package = 'fastiot'
modules = [
    *find_modules(package='fastiot_sample_services', cache='fastiot-cache', extra_caches=['fastiot-cache:latest'])
]

test_package = 'fastiot_test'
test_config = 'fastiot_test_env'

compile_lib = 'only_source'
