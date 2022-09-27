""" Module to hold basic environment variables """
import logging
import os
from typing import Optional

from fastiot.cli.common.infrastructure_services import MongoDBService, MariaDBService, InfluxDBService, \
    TimeScaleDBService, NatsService
from fastiot.env import *


class BasicEnv:
    """
    Holds the default environment variables for the fastIoT framework.

    Use the properties from :func:`fastiot.env.fastiot_basic_env` to read the values in an easy manner within your code.
    """

    @property
    def config_dir(self):
        """ .. envvar:: FASTIOT_CONFIG_DIR

        Use to get/set the config dir, defaults to :file:`/etc/fastiot` if not set.

        This should point to your deployment configuration dir, which is also copied to target either manually or using
        the :func:`fastiot.cli.commands.deploy.deploy` CLI command.

        This variable is either handled in your container or can be overwritten using e.g. a
        :file:`local-testing-overwrite.env` in your config-dir. See the Tutorial :ref:`label-setting-up-pycharm` for
        more details about setting env vars within PyCharm.

        On automatic project setups everything should work out fine for you!
        """
        return os.getenv(FASTIOT_CONFIG_DIR, '/etc/fastiot')

    @property
    def log_level_no(self) -> int:
        """ .. envvar:: FASTIOT_LOG_LEVEL_NO

        This environment variable is used to set the logging Level.
        Level for logging s. https://docs.python.org/3/library/logging.html#logging-levels
        """
        return int(os.getenv(FASTIOT_LOG_LEVEL_NO, logging.INFO))

    @property
    def volume_dir(self) -> str:
        """ .. envvar:: FASTIOT_VOLUME_DIR

        Use this variable to set the mount dir for your project
        """
        return os.getenv(FASTIOT_VOLUME_DIR, '/var/fastiot')

    @property
    def service_id(self) -> str:
        """ .. envvar:: FASTIOT_SERVICE_ID

        Use this variable to differentiate between multiple instances of the same service. The result is available as
        ``self.service_id``. It is for example used to read a configuration file for each service with
        :func:`fastiot.helpers.read_yaml.read_config`. See
        """
        return os.getenv(FASTIOT_SERVICE_ID, '')
    @property
    def log_dir(self) -> str:
        return os.path.join(self.volume_dir, 'logs')

    @property
    def error_logfile(self) -> str:
        return os.path.join(self.log_dir, 'error.log')


class BrokerEnv:
    """
    Environment variables for the message broker

    Use the properties from :func:`fastiot.env.FASTIOT_NATS_env` to read the values in an easy manner within your
    code.
    """

    @property
    def host(self) -> str:
        """
        .. envvar:: FASTIOT_NATS_HOST

        Use to get/set the broker host. This is usually either ``nats`` within the docker network or ``localhost``
        when developing against a local broker.
        """
        return os.environ.get(FASTIOT_NATS_HOST, 'localhost')

    @property
    def port(self) -> int:
        """
        .. envvar:: FASTIOT_NATS_PORT

        Use to get/set the broker port, defaults to 4222.
        """
        return int(os.getenv(FASTIOT_NATS_PORT, NatsService().get_default_port()))

    @property
    def default_timeout(self) -> float:
        """ .. envvar:: FASTIOT_NATS_DEFAULT_TIMEOUT

        Use to get/set the broker timeout in seconds, defaults to 30.
        """
        return float(os.getenv(FASTIOT_NATS_DEFAULT_TIMEOUT, '30'))


class MongoDBEnv:
    """
    Environment variables for mongodb :ref:`MongoDB Service <MongoDBService>`

    Use the properties from :func:`fastiot.env.env.env_mongodb` to read the values in an easy manner within your
    code.
    """

    @property
    def host(self) -> str:
        """ .. envvar:: FASTIOT_MONGO_DB_HOST

        Use to get/set the mongo database host. This is usually either ``mongodb`` within the docker network or
        ``localhost`` when developing against a local mongodb.
        """
        return os.getenv(FASTIOT_MONGO_DB_HOST, 'localhost')

    @property
    def port(self) -> int:
        """ .. envvar:: FASTIOT_MONGO_DB_PORT

        Use to get/set the mongodb port, defaults to 27017. """
        return int(os.getenv(FASTIOT_MONGO_DB_PORT, MongoDBService().get_default_port()))

    @property
    def user(self) -> Optional[str]:
        """ .. envvar:: FASTIOT_MONGO_DB_USER

        Use to get/set the mongodb user.
        """
        return os.getenv(FASTIOT_MONGO_DB_USER, MongoDBService().get_default_env(FASTIOT_MONGO_DB_USER))

    @property
    def password(self) -> Optional[str]:
        """ .. envvar:: FASTIOT_MONGO_DB_PASSWORD

        Use to get/set the mongodb password.
        """
        return os.getenv(FASTIOT_MONGO_DB_PASSWORD, MongoDBService().get_default_env(FASTIOT_MONGO_DB_PASSWORD))

    @property
    def auth_source(self) -> Optional[str]:
        """ .. envvar:: FASTIOT_MONGO_DB_AUTH_SOURCE

        Use to get/set the mongodb auth source, which is a database name which is needed for authentication.
        """
        return os.getenv(FASTIOT_MONGO_DB_AUTH_SOURCE, 'admin')

    @property
    def name(self) -> str:
        """ .. envvar:: FASTIOT_MONGO_DB_NAME

        Use to get/set the name of mongodb database.
        """
        return os.getenv(FASTIOT_MONGO_DB_NAME, "fastiot")

    @property
    def is_configured(self) -> bool:
        """
        Use to indicate if the mongodb is configured, it is not bound to any environment variable
        """
        if FASTIOT_MONGO_DB_HOST in os.environ:
            return True
        return False


class MongoDBColConstants:
    """
    Environment variables for mongodb collection

    Use the properties from :func:`fastiot.env.env_mongodb_cols` to read the values in an easy manner within your
    code.
    """
    @property
    def time_series(self) -> str:
        """ ..envvar:: FASTIOT_MONGO_DB_TIME_SERIES_COL

        """
        return os.getenv(FASTIOT_MONGO_DB_TIME_SERIES_COL, 'time_series')


class MariaDBEnv:
    """
    Environment variables for mariadb :ref:`MariaDB Service <MariaDBService>`

    Use the properties from :func:`fastiot.env.env.env_mariadb` to read the values in an easy manner within your
    code. This will provide the environment variables needed for
    :func:`fastiot.db.mariadb_helper_fn.open_mariadb_connection_from_env`
    """

    @property
    def host(self) -> str:
        """ .. envvar:: FASTIOT_MARIA_DB_HOST

        Use to get/set the maria database host. This is usually either ``mariadb`` within the docker network or
        ``localhost`` when developing against a local mariadb.
        """
        return os.getenv(FASTIOT_MARIA_DB_HOST, 'localhost')

    @property
    def port(self) -> int:
        """ .. envvar:: FASTIOT_MARIA_DB_PORT

        Use to get/set the mariadb port, defaults to 3306. """
        return int(os.getenv(FASTIOT_MARIA_DB_PORT, MariaDBService().get_default_port()))

    @property
    def user(self) -> str:
        """ .. envvar:: FASTIOT_MARIA_DB_USER

        Use to get/set the mariadb user.
        """
        return os.getenv(FASTIOT_MARIA_DB_USER, 'root')

    @property
    def password(self) -> Optional[str]:
        """ .. envvar:: FASTIOT_MARIA_DB_PASSWORD

        Use to get/set the mariadb password.
        """
        return os.getenv(FASTIOT_MARIA_DB_PASSWORD, MariaDBService().get_default_env(FASTIOT_MARIA_DB_PASSWORD))

    @property
    def schema_fastiotlib(self) -> str:
        """ .. envvar:: FASTIOT_MARIA_DB_SCHEMA_FASTIOTLIB

        Use to get/set the mariadb schema.
        """
        return str(os.getenv(FASTIOT_MARIA_DB_SCHEMA_FASTIOTLIB))

    @property
    def is_configured(self) -> bool:
        if FASTIOT_MARIA_DB_HOST in os.environ:
            return True
        return False


class InfluxDBEnv:
    """
    Environment variables for influxdb :ref:`InfluxDB Service <InfluxDBService>`

    Use the properties from :func:`fastiot.env.env.env_influxdb` to read the values in an easy manner within your
    code. For connecting to InfluxDB, which is started with a token, you only need host, port and token.
    username and password are used for browser GUI.
    """

    @property
    def host(self) -> str:
        """ .. envvar:: FASTIOT_INFLUX_DB_HOST

        Use to get/set the influx database host. This is usually either ``influxdb`` within the docker network or
        ``localhost`` when developing against a local influxdb.
        """
        return os.getenv(FASTIOT_INFLUX_DB_HOST, 'localhost')

    @property
    def port(self) -> int:
        """ .. envvar:: FASTIOT_INFLUX_DB_PORT

        Use to get/set the influxdb port, defaults to 8086. """
        return int(os.getenv(FASTIOT_INFLUX_DB_PORT, InfluxDBService().get_default_port()))

    @property
    def user(self) -> str:
        """ .. envvar:: FASTIOT_INFLUX_DB_USER

        Use to get/set the influxdb username, default to 'influx_db_admin'.
        This env var is only used for browser login, not for connecting from fastiot framework.
        """
        return str(os.getenv(FASTIOT_INFLUX_DB_USER, 'influx_db_admin'))

    @property
    def password(self) -> str:
        """ .. envvar:: FASTIOT_INFLUX_DB_PASSWORD

        Use to get/set the influxdb password, default to 'mf9ZXfeLKuaL3HL7w'.
        This env var is only used for browser login, not for connecting from fastiot framework.
        password for InfluxDB must be complex, otherwise InfluxDB won't be started.
        """
        return str(os.getenv(FASTIOT_INFLUX_DB_PASSWORD, InfluxDBService().get_default_env(FASTIOT_INFLUX_DB_PASSWORD)))

    @property
    def token(self) -> Optional[str]:
        """.. envvar:: FASTIOT_INFLUX_DB_TOKEN

        InfluxDB API token with permission to query (read) buckets and create (write) authorizations for devices
        """
        return os.getenv(FASTIOT_INFLUX_DB_TOKEN, InfluxDBService().get_default_env(FASTIOT_INFLUX_DB_TOKEN))


class TimeScaleDBEnv:
    """
    Environment variables for timescaledb :ref:`TimeScaleDB Service <TimeScaleDBService>`

    Use the properties from :func:`fastiot.env.env.env_timescaledb` to read the values in an easy manner within your
    code.
    """

    @property
    def host(self) -> str:
        """ .. envvar:: FASTIOT_TIME_SCALE_DB_HOST

        Use to get/set the time scale database host. This is usually either ``timescaledb`` within the docker
        network or ``localhost`` when developing against a local time_scale_db.
        """
        return os.getenv(FASTIOT_TIME_SCALE_DB_HOST, 'localhost')

    @property
    def port(self) -> int:
        """ .. envvar:: FASTIOT_TIME_SCALE_DB_PORT

        Use to get/set the time scale db port, defaults to 5432.
        """
        return int(os.getenv(FASTIOT_TIME_SCALE_DB_PORT, TimeScaleDBService().get_default_port()))

    @property
    def user(self) -> Optional[str]:
        """ .. envvar:: FASTIOT_TIME_SCALE_DB_USER

        Use to get/set the time scale db user.
        """
        return os.getenv(FASTIOT_TIME_SCALE_DB_USER, TimeScaleDBService().get_default_env(FASTIOT_TIME_SCALE_DB_USER))

    @property
    def password(self) -> Optional[str]:
        """ .. envvar:: FASTIOT_TIME_SCALE_DB_PASSWORD

        Use to get/set the time scale db password.
        """
        return os.getenv(FASTIOT_TIME_SCALE_DB_PASSWORD,
                         TimeScaleDBService().get_default_env(FASTIOT_TIME_SCALE_DB_PASSWORD))

    @property
    def database(self) -> str:
        """ .. envvar:: FASTIOT_TIME_SCALE_DB_DATABASE

        Use to get/set the time scale db database.
        """
        return str(os.getenv(FASTIOT_TIME_SCALE_DB_DATABASE,
                             TimeScaleDBService().get_default_env(FASTIOT_TIME_SCALE_DB_DATABASE)))


env_basic = BasicEnv()
env_broker = BrokerEnv()
env_mongodb = MongoDBEnv()
env_mongodb_cols = MongoDBColConstants()
env_mariadb = MariaDBEnv()
env_influxdb = InfluxDBEnv()
env_timescaledb = TimeScaleDBEnv()
