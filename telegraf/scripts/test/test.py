# import zipfile
# import xmltodict
# def analysis(path):
#     z = zipfile.ZipFile(path, 'r')
#     for f in z.namelist():
#         xml_file = z.read(f)
#         xml_dict = xmltodict.parse(xml_file)
#         cq_data = []
#         for item in xml_dict['rdml']['experiment']['run']['react']:
#             adp_data = []
#             mdp_data = []
#             for item_data in item['data']:
#                 cq_data.append('insert pcr_rdml_cq,sample=%s,tar=%s,ID=%s,excl=%s value=%s' % (item['sample']['@id'],item_data['tar']['@id'],'%03d' % int(item['@id']),item_data.get('excl', 'FALSE'),item_data['cq'] if item_data['cq'] != 'Infinity' else 0))
#                 for adp in item_data['adp']:
#                     adp_data.append('insert pcr_rdml_adp,sample=%s,tar=%s,cyc=%s fluor=%s' % (item['sample']['@id'],item_data['tar']['@id'],adp['cyc'],adp['fluor']))
#                 if item_data.get('mdp'):
#                     for mdp in item_data['mdp']:
#                         data = {
#                             'measurement': 'pcr_rdml_mdp',
#                             'tags': {
#                                 'sample': item['sample']['@id'],
#                                 'tar': item_data['tar']['@id'],
#                                 'tmp': mdp['tmp'],
#                             },
#                             'fields': {
#                                 'fluor': mdp['fluor']
#                             }
#                         }
#                         mdp_data.append(data)
#             try:
#                 print('\n'.join(adp_data))
#                 #self.influxdb_cli.write_points(adp_data)
#                 #self.influxdb_cli.write_points(mdp_data)
#             except Exception as e:
#                 self.logger.error(str(e))
#         try:
#             pass
#             #self.influxdb_cli.write_points(cq_data)
#         except Exception as e:
#             self.logger.error(str(e))
# analysis('demo.rdml')


import unittest
import os
import sys
import shutil
import time

sys.path.append('/opt/grpc')
sys.path.append('/opt/scripts')

from conf import conf
from db import influxdb_cli


class Test(unittest.TestCase):
    def test_fastq_watch(self):
        test_fastq_file = 'test.fastq'
        data_dir = conf.get('ont').get('fastq_watch_path')
        cell = 'TEST-CELL'
        chip = 'TEST-CHIP'
        fastq_dir = os.path.join(data_dir, cell, chip, 'fastq_pass')
        if not os.path.exists(fastq_dir):
            os.makedirs(fastq_dir)
        tmp_fastq_file = os.path.join(fastq_dir, '%s.tmp' % test_fastq_file)
        fastq_file = tmp_fastq_file[:-4]
        shutil.copyfile(test_fastq_file, tmp_fastq_file)
        shutil.move(tmp_fastq_file, fastq_file)
        time.sleep(1)
        sql = "select * from fastq_watch where cell = '%s' and dir = '%s' and path = '%s'" % (cell, fastq_dir, fastq_file)
        res = influxdb_cli.query(sql)
        self.assertGreater(len(list(res.get_points())), 0)


if __name__ == '__main__':
    suite = unittest.TestSuite()
    tests = unittest.TestLoader().loadTestsFromTestCase(Test)
    suite.addTests(tests)
    runner = unittest.TextTestRunner()
    runner.run(suite)
