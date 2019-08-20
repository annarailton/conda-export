"""Converts the output of

    conda list --show-channel-urls

to an env.yml file, correctly mapping dependencies with non-default channels to
those channels e.g.

# Name                    Version                   Build  Channel
airflow                   1.10.3post1              py36_0    conda-forge
airflow-with-mysql        1.10.3                        1    conda-forge
alembic                   0.9.10                   py36_0    defaults

to

dependencies:
- conda-forge::airflow-with-mysql=1.10.3=1
- conda-forge::airflow=1.10.3post1=py36_0
- alembic=0.9.10=py36_0

"""
import argparse
import os
import subprocess

from collections import OrderedDict

import ruamel.yaml  # correct indentation

if __name__ == '__main__':

    args_parser = argparse.ArgumentParser()
    args_parser.add_argument(
        '-n',
        '--name',
        dest='env_name',
        help='conda environment name (must exist)',
        type=str,
        required=True,
    )
    args_parser.add_argument(
        '-o',
        '--output',
        dest='output',
        help='destination of output file (default: env_$ENV_NAME.yml in $PWD)',
        type=str)

    args = args_parser.parse_args()

    # Check conda env exists
    proc = subprocess.Popen(['conda', 'env', 'list'], stdout=subprocess.PIPE)
    outs, _ = proc.communicate()
    output = outs.decode('utf-8')
    if args.env_name not in output.split():
        raise IOError(f'There is no enviroment called {args.env_name}')

    if not args.output:
        output = f'env_{args.env_name}.yml'
    else:
        output = args.output

    # Get dependencies
    proc = subprocess.Popen(
        ['conda', 'list', '-n', args.env_name, '--show-channel-urls'],
        stdout=subprocess.PIPE)
    outs, _ = proc.communicate()

    # Populate dict
    env_data = OrderedDict.fromkeys(
        ['name', 'channels', 'dependencies', 'prefix'])
    env_data['channels'] = ['defaults']
    dependency_list = []
    dependency_with_channels = []

    rows = outs.decode('utf-8').split('\n')
    rows = list(filter(None, rows))  # remove empty strings (= empty lines)

    for row in rows:
        if row.startswith('#'):
            if 'packages in environment' in row:
                env_loc = row.split()[-1].replace(':', '')
                env_data['prefix'] = env_loc
                env_data['name'] = os.path.basename(env_loc)
            continue
        res = row.split()
        if res[-1] == 'defaults':
            dependency_list.append('='.join(res[0:-1]))
        else:
            dependency_with_channels.append(tuple(res))

    dependency_with_channels = sorted(
        dependency_with_channels, key=lambda x: x[3])  # sort by channel
    dependency_with_channels_list = [
        res[-1] + '::' + '='.join(res[0:-1])
        for res in dependency_with_channels
    ]
    env_data['dependencies'] = dependency_with_channels_list + dependency_list

    class MyRepresenter(ruamel.yaml.representer.RoundTripRepresenter):
        pass

    ruamel.yaml.add_representer(
        OrderedDict, MyRepresenter.represent_dict, representer=MyRepresenter)

    yaml = ruamel.yaml.YAML()
    yaml.Representer = MyRepresenter
    yaml.indent(offset=2)
    with open(output, 'w') as f_out:
        yaml.dump(env_data, f_out)

    print(f'Written env details to {output}')
