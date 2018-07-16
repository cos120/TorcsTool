from collections import defaultdict as dict
track_category_name = dict(list)
all_track_names = []
all_log_track_names = []
with open(__file__.replace('constant.py','track_f.txt')) as f:
    for line in f:
        line = line.strip()
        track_path , _track_category , _track_name = line.split('\t')
        all_track_names.append(track_path)
        all_log_track_names.append('{}_{}'.format(_track_category,_track_name))
        track_category_name[_track_category].append(_track_name)
category = list(track_category_name.keys())
