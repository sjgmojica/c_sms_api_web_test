#!/bin/sh

working_dir=/home/noc/projects/chikka_sms_api/standalone/offline_updaters
# working_dir=/home/jhesed/ChikkaSMS_API/standalone.2013-12-19/offline_updaters

echo "started processing CHIKKA SMS API updaters"

cd $working_dir

export LD_LIBRARY_PATH=/opt/lib:/opt/lib/mysql:$LD_LIBRARY_PATH; /opt/bin/python $working_dir/start_updaters.py --config=prod > /dev/null 2>&1&
# export LD_LIBRARY_PATH=/opt/lib:/opt/lib/mysql:$LD_LIBRARY_PATH; /opt/bin/python $working_dir/start_updaters.py --config=debug > /dev/null 2>&1&

echo "finished processing CHIKKA SMS API updaters"

