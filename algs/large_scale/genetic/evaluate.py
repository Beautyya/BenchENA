import hashlib, time
from algs.large_scale.genetic.population import Population, ArcText
import os
from compute.file import get_algo_local_dir, get_local_path
from compute.process import dispatch_to_do
from compute import Config_ini
from compute.gpu import gpus_all_available
from comm.utils import CacheToResultFile
from algs.large_scale.utils import Utils


class FitnessEvaluate(object):
    def __init__(self, individuals, log):
        self.individuals = individuals
        self.log = log

    def generate_to_python_file(self, test=False):
        for dna in self.individuals:
            arc = ArcText()
            arc.transform(dna)
            dna.uuid = hashlib.sha224(arc.__str__().encode('utf-8')).hexdigest()
            write_script(dna.individual_id, arc.to_pytorch_file(), test)

    def evaluate(self):
        _map = Utils.load_cache_data()
        _count = 0
        for dna in self.individuals:
            if dna.fitness > 0:
                CacheToResultFile.do(dna.individual_id, float(dna.fitness))
            else:
                _uuid = dna.uuid
                if _uuid in _map:
                    _count += 1
                    _acc = _map[_uuid]
                    CacheToResultFile.do(dna.individual_id, float(_acc))
                    dna.fitness = float(_acc)

        for dna in self.individuals:
            if dna.fitness < 0:
                _id = dna.individual_id
                _uuid = dna.uuid
                dispatch_to_do(_id, _uuid)

        all_have_been_evaluated = False
        while all_have_been_evaluated is not True:
            time.sleep(120)
            all_have_been_evaluated = gpus_all_available()


def write_script(_id, _str, test=False):
    if not test:
        file_name = '%s/%s.py' % (os.path.join(get_algo_local_dir(), 'scripts'), _id)
    else:
        file_name = '%s/large_scale_%s.py' % (os.path.join(get_local_path(), 'example'), _id)
    with open(file_name, 'w') as f:
        f.write(_str)
