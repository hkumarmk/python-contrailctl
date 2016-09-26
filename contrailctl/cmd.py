import argparse
import sys
from contrailctl.config import Configurator
from contrailctl.map import CONTROLLER_PARAM_MAP
from contrailctl.runner import Runner


class ConfigManager(object):
    # This name (component_map) may not make sense here, in any time we wanted to handle individual services within
    # the container with contrailctl. Here the assumption is that contrailctl always handle high level configs, but
    # it may ended up managing individual components later.
    COMPONENT_PARAM_MAP = {
        "controller": CONTROLLER_PARAM_MAP,
    }

    # NOTE: it may make sense to have some of these params to be get from user in later point. But currently they are
    # constants
    RUNNER_PARAMS = dict(
        inventory='/contrail-ansible/playbooks/inventory/all-in-one',
        playbook='/contrail-ansible/playbooks/site.yml',
        tags=['provision', 'configure'],
        verbosity=0
    )

    def __init__(self, config_file, component):
        self.component = component
        self.config_file = config_file
        self.param_map = self.COMPONENT_PARAM_MAP[component]

    def sync(self):
        component_config = Configurator(self.config_file, self.param_map)
        config_dict = component_config.map({})
        ansible_runner = Runner(run_data=config_dict, **self.RUNNER_PARAMS)
        stats = ansible_runner.run()
        return stats


def main(args=sys.argv[1:]):
    ap = argparse.ArgumentParser(description="Contrailctl")
    sp = ap.add_subparsers(dest="resource", help="Resource to manage")
    p_config = sp.add_parser("config", help="manage configuration")
    sp_config = p_config.add_subparsers(dest="action")
    p_config_sync = sp_config.add_parser("sync", help="Sync the config")
    p_config_cfg = p_config_sync.add_argument("-f", "--config-file", type=str,
                                         help="Master config file path")
    p_config_comp = p_config_sync.add_argument("-c", "--component", type=str,
                                         choices=["controller"],
                                         default="controller",
                                         help="Component[s] to be configured")
    args = ap.parse_args()

    if not args.config_file:
        args.config_file = "/etc/contrailctl/%s.conf" % args.component

    cm = ConfigManager(args.config_file, args.component)
    stats = cm.sync()

if __name__ == '__main__':
    main(sys.argv[1:])
