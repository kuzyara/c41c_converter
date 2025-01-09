# c41c_converter
конвертер замеров для [coverage41c](https://github.com/1c-syntax/Coverage41C)

написал конвертер из 
```xml
<file path="/242cb07d-3d2b-4689-b590-d3ed23ac9d10/a637f77f-3840-441d-a1c3-699c8c5cb7e0">
    <lineToCover covered="true" lineNumber="4"/>
    <lineToCover covered="true" lineNumber="3"/>
</file>
```
в 
```xml
<file path="DataProcessors/ЖурналДокументовНМА2_4/Forms/ДокументыПоНМА/Ext/Form/Module.bsl">
    <lineToCover covered="true" lineNumber="4"/>
    <lineToCover covered="true" lineNumber="3"/>
</file>
```
работает как с исходниками в формате выгрузки в xml, так и с edt (mdo)

пример использования
```console
> .\c41c_convert.py --config-path C:\test\src --measures-path C:\Users\Kuznetsov_NA\Desktop\temp\coverage41c\Zamer\pff\xml --output C:\test\res
Parsing .xml: 100%|████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 21794/21794 [00:05<00:00, 4323.48it/s]
Parsing .mdo: 0it [00:00, ?it/s]
Результат записан в C:\test\res\openformsdataprocessors\genericCoverage.xml
```
