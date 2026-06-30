import h5py
import json

f = h5py.File('ml_models/mobilenetv2_chili_final1.h5', 'r+')
config = json.loads(f.attrs['model_config'])

def patch_dtype(obj):
    if isinstance(obj, dict):
        if 'module' in obj and obj['module'] == 'keras' and obj.get('class_name') == 'DTypePolicy':
            return obj['config']['name']
        for k, v in obj.items():
            obj[k] = patch_dtype(v)
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            obj[i] = patch_dtype(v)
    return obj

config = patch_dtype(config)
f.attrs['model_config'] = json.dumps(config).encode('utf-8')
f.close()
print("DTypePolicy Patch Applied!")
