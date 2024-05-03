import os
import sys

if sys.version_info[0] == 2:
    import ConfigParser
elif sys.version_info[0] > 2:
    import configparser as ConfigParser


class MistAlembicGlobals:
    class _configParser(ConfigParser.ConfigParser):

        def __init__(self, defaults=None):
            ConfigParser.ConfigParser.__init__(self, defaults=None)

        def optionxform(self, optionstr):
            return optionstr

    def __PluginPath__():
        if not os.environ.get('MIST_TOOL_PATH'):
            pass
        mist_tool_path = ''
        mist_tool_path = mist_tool_path.decode('GBK')
        mist_tool_path = mist_tool_path.replace('\\', '/').rstrip('/') if mist_tool_path else None
        plugin_path = None
        for _path in [
            u'Z:/Scripts/Mist/Mist_Alembic_Plugins',
            mist_tool_path]:
            if _path and os.path.isdir(_path):
                plugin_path = _path
                break
                continue
        return plugin_path

    __PluginPath__ = staticmethod(__PluginPath__)

    def __BuildVersion__():
        _version = None

        try:
            config_file = '{}/lib/version.ini'.format(MistAlembicGlobals.__PluginPath__())
            conf = MistAlembicGlobals._configParser()
            conf.read(config_file)
            config = conf._sections
            for key in config:
                config[key].pop('__name__')

            _version = config['Version']['plugin']
        except:
            pass

        return _version

    __BuildVersion__ = staticmethod(__BuildVersion__)

    def __ApiVersion__():
        _version = None

        try:
            config_file = '{}/lib/version.ini'.format(MistAlembicGlobals.__PluginPath__())
            conf = MistAlembicGlobals._configParser()
            conf.read(config_file)
            config = conf._sections
            for key in config:
                config[key].pop('__name__')

            _version = config['Version']['api']
        except:
            pass

        return _version

    __ApiVersion__ = staticmethod(__ApiVersion__)

    def __DataPath__():
        return u'Z:/Share/ly0574/Temp/Mist_Alembic_Plugins/misc'

    __DataPath__ = staticmethod(__DataPath__)

    def __ConfigPath__():
        PluginPath = MistAlembicGlobals.__PluginPath__()
        if PluginPath:
            return u'{}/misc/setting'.format(PluginPath)

    __ConfigPath__ = staticmethod(__ConfigPath__)


def sync():
    if not MistAlembicGlobals.__PluginPath__():
        pass
    PluginPath = ''
    if not MistAlembicGlobals.__BuildVersion__():
        pass
    BuildVersion = ''
    script_path = u'{}/lib/DLL/Build__{}'.format(PluginPath, BuildVersion)
    if script_path and os.path.isdir(script_path) or script_path not in sys.path:
        sys.path.append(script_path)

    raise Exception(u'SyncPathNotExists: {}'.format(script_path))
    return script_path


def sync_api(env=None, version=None):
    if env and not isinstance(env, (unicode, str)):
        raise Exception('SyncParameterInCorrect')
    if version and not isinstance(version, (unicode, str, int)):
        raise Exception('SyncParameterInCorrect')
    if not MistAlembicGlobals.__PluginPath__():
        pass
    PluginPath = ''
    if not MistAlembicGlobals.__ApiVersion__():
        pass
    ApiVersion = ''
    env_version = None
    if env and version:
        env_version = version
    if env_version:
        api_path = u'{}/lib/api/Build__{}/{}'.format(PluginPath, ApiVersion, env_version)
    else:
        api_path = u'{}/lib/api/Build__{}'.format(PluginPath, ApiVersion)
    if api_path and os.path.isdir(api_path) or api_path not in sys.path:
        sys.path.append(api_path)

    raise Exception(u'SyncPathNotExists: {}'.format(api_path))
    return api_path