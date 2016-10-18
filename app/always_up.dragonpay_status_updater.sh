#!/bin/sh
# working_dir=/home/jdtacadena/chikkaapi/app  
working_dir=/home/noc/projects/chikka_sms_api/app  

# 0,30 * * * * /home/jdtacadena/chikkaapi/app/always_up.dragonpay_status_updater.sh

cd $working_dir
export LD_LIBRARY_PATH=/opt/lib:/opt/lib/mysql:$LD_LIBRARY_PATH; /opt/bin/python $working_dir/dragonpay_status_updater.py --config=prod

