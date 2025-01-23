import argparse
from glob import glob
from tqdm import tqdm
import os
import re
from xml.etree import ElementTree


def parse_args():
    parser = argparse.ArgumentParser(description='Запуск формирования отчета')

    parser.add_argument("--output", help="", required=False, dest="path_to_output")
    parser.add_argument("--config-path", help="", required=False, dest="path_to_conf")
    parser.add_argument("--measures-path", help="file or dir", required=False, dest="path_to_measures")

    return parser.parse_known_args()


def get_abs_path(path_):
    return os.path.join(os.path.dirname(os.path.realpath(__file__)), path_)


def get_dict_from_uuids(path_to_uuids, offset=0):
    with open(path_to_uuids, 'r', encoding="utf-8-sig") as file_uuids:
        input_uuids = file_uuids.readlines()
    new_dict = {}
    for line in input_uuids:
        # line = line.replace(r"\ufeff","")
        split_line = line.split(";")
        if len(split_line) >= 3+offset:
            key = re.search("[^\n]+", split_line[0])[0]
            value = re.search("[^\n]+", split_line[2+offset])[0]
            new_dict[key] = value
    return new_dict


if __name__ == '__main__':

    args, unknown_args = parse_args()
    params = {"path_to_conf": args.path_to_conf,
              "measure_dirs": args.path_to_measures,
              "uuid_to_path": get_abs_path("lib\\module_types.txt"),
              "uuids_obj_path": {}}

    params["uuids_module_name"] = get_dict_from_uuids(params["uuid_to_path"])
    params["uuids_xml_module_name"] = get_dict_from_uuids(params["uuid_to_path"], 1)

    # для исходников в формате выгрузки в файлы xml
    all_xml = glob(params['path_to_conf'] + '\\**\\*.xml', recursive=True)
    for xml_filepath in tqdm(all_xml, desc="Parsing .xml"):
        with open(xml_filepath, 'r', encoding='utf-8-sig') as xml_file:
            # "C:\test\src\Documents\НачислениеРеверсивногоНДС.xml" ->
            # "C:\test\src\Documents\НачислениеРеверсивногоНДС\Ext\ManagerModule.bsl"
            # "C:\test\src\Documents\НачислениеРеверсивногоНДС\Forms\ФормаДокумента.xml" ->
            # "C:\test\src\Documents\НачислениеРеверсивногоНДС\Forms\ФормаДокумента\Ext\Form\Module.bsl"
            obj_dir = os.path.dirname(xml_filepath)
            base = os.path.basename(xml_filepath)
            obj_name = os.path.splitext(base)[0]
            xml_data = xml_file.read()
            obj_uuid_pattern = r'(?<=uuid\=\").*?(?=\")'
            obj_uuid_match = re.search(obj_uuid_pattern, xml_data)
            if obj_uuid_match:
                obj_uuid = obj_uuid_match.group()
                params["uuids_obj_path"][obj_uuid] = {"obj_dir": obj_dir, "obj_name": obj_name, "type": "xml"}

    # для исходников в формате edt
    all_mdo = glob(params['path_to_conf'] + '\\**\\*.mdo', recursive=True)
    for mdo_filepath in tqdm(all_mdo, desc="Parsing .mdo"):
        with open(mdo_filepath, 'r', encoding='utf-8-sig') as mdo_file:
            obj_dir = os.path.dirname(mdo_filepath)
            mdo_data = mdo_file.read()
            obj_uuid_pattern = r'(?<=uuid\=\").*?(?=\")'
            obj_uuid_match = re.search(obj_uuid_pattern, mdo_data)
            if obj_uuid_match:
                obj_uuid = obj_uuid_match.group()
                params["uuids_obj_path"][obj_uuid] = {"obj_dir": obj_dir, "type": "mdo"}
            # forms uuid=
            forms_uuid_pattern = r'(?<=forms uuid\=\").*?(?=\")'
            forms_uuid_matches = re.finditer(forms_uuid_pattern, mdo_data)
            for forms_uuid_match in forms_uuid_matches:
                form_uuid = forms_uuid_match.group()
                form_name_pattern = r'(?<=<name>).+(?=</name>)'
                form_name_match = re.search(form_name_pattern, mdo_data[forms_uuid_match.start():])
                form_name = form_name_match.group()
                form_dir = os.path.join(*[obj_dir, "Forms", form_name])
                params["uuids_obj_path"][form_uuid] = {"obj_dir": form_dir, "type": "mdo"}

    all_measures = glob(params["measure_dirs"] + '\\**\\*.xml', recursive=True) if os.path.isdir(
        params["measure_dirs"]) else [params["measure_dirs"]]
    for file in tqdm(all_measures):
        with open(file, 'r', encoding='utf-8', errors='ignore') as file_measure:
            doc = ElementTree.parse(file_measure)
            file_nodes = []
            # format COBERTURA
            for file_node in doc.findall('.//class'):
                file_nodes.append(file_node)
                key = "filename"
            # format GENERIC_COVERAGE
            for file_node in doc.findall('.//file'):
                file_nodes.append(file_node)
                key = "path"
            # преобразуем "/b323fada-5de9-42be-99ee-32ceaa9771a5/d5963243-262e-4398-b4d7-fb16d06484f6"
            # в "CommonModules/ОбщийМодуль1/Ext/Module.bsl"
            for file_node in file_nodes:
                path = file_node.attrib[key]
                obj_uuid = path.split("/")[-2]
                module_uuid = path.split("/")[-1]
                if obj_uuid not in params["uuids_obj_path"]:
                    print(f"Пропущен модуль {path}")
                    continue
                if module_uuid not in params["uuids_module_name"]:
                    print(f"Пропущен тип {path}")
                    continue
                uuid_obj = params["uuids_obj_path"][obj_uuid]
                file_dir = uuid_obj["obj_dir"]
                if uuid_obj["type"] == "xml":
                    file_name_tmpl = params["uuids_xml_module_name"][module_uuid]
                    file_name = file_name_tmpl.format(obj_name=uuid_obj["obj_name"])
                    file_path = os.path.normpath(os.path.join(file_dir, file_name))
                else:  # mdo
                    file_name = params["uuids_module_name"][module_uuid]
                    file_path = os.path.normpath(os.path.join(file_dir, file_name))
                if os.path.exists(file_path):
                    rel_path = os.path.relpath(file_path, params['path_to_conf'])
                    file_node.set(key, rel_path)
                else:
                    print(f"Не найден файл {path}")
                    continue
        if os.path.isfile(params["measure_dirs"]):
            base_path = os.path.basename(params["measure_dirs"])
        else:
            base_path = str(os.path.relpath(file, params["measure_dirs"]))
        output_path = os.path.join(args.path_to_output, base_path)

        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        doc.write(output_path, encoding="UTF-8", xml_declaration=True)

        print(f"Результат записан в {output_path}")
