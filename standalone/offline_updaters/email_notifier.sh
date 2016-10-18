#!/bin/sh

working_dir=/home/noc/projects/chikka_sms_api/standalone/offline_updaters
# working_dir=/home/jhesed/ChikkaSMS_API/standalone.2013-12-19/offline_updaters

echo "started processing CHIKKA SMS API email notifiers"
echo $working_dir

cd $working_dir

echo "going to directory"

export LD_LIBRARY_PATH=/opt/lib:/opt/lib/mysql:$LD_LIBRARY_PATH; /opt/bin/python $working_dir/start_email_notifiers.py --config=prod > /dev/null 2>&1&
# export LD_LIBRARY_PATH=/opt/lib:/opt/lib/mysql:$LD_LIBRARY_PATH; /opt/bin/python $working_dir/start_email_notifiers.py --config=debug > /dev/null 2>&1&

echo "finished processing CHIKKA SMS API email notifiers"
