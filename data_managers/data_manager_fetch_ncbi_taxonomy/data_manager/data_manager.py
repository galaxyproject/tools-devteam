import json
import datetime
import argparse
import os
import shutil

parser = argparse.ArgumentParser(description='Create data manager json.')
parser.add_argument('--out', dest='output', action='store', help='JSON filename')
parser.add_argument('--name', dest='name', action='store', default=str(datetime.date.today()), help='Data table entry unique ID')

args = parser.parse_args()

def main(args):
    data_manager_entry = {}
    data_manager_entry['value'] = args.name.lower()
    data_manager_entry['name'] = args.name
    data_manager_entry['path'] = '.'
    data_manager_json = dict(data_tables=dict(ncbi_taxonomy=data_manager_entry))
    params = json.loads(open(args.output).read())
    target_directory = params['output_data'][0]['extra_files_path']
    os.mkdir(target_directory)
    output_path = os.path.abspath(os.getcwd())
    for filename in [ 'names.dmp', 'nodes.dmp' ]:
        shutil.move(os.path.join(output_path, filename), target_directory)
    file(args.output, 'w').write(json.dumps(data_manager_json))

if __name__ == '__main__':
    main(args)
