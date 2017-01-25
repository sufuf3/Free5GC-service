#!/usr/bin/env python

#   Author: Mike Adolphs, 2009
#   Blog: http://www.matejunkie.com/
#
#   This program is free software; you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation; version 2 of the License only!
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program; if not, write to the Free Software
#   Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

import sys
import urllib

def retrieve_status_page():
    statusPage = "http://localhost/server-status?auto"
    try:
        retrPage = urllib.urlretrieve(statusPage, '/tmp/server-status.log')
        return True
    except:
        return False

def parse_status_page():
    """Main parsing function to put the server-status file's content into
       a dictionary."""

    file = open('/tmp/server-status.log', 'r')
    line = file.readline()
    dictStatus = {}
    counter = 1

    while line:
        line = line.strip()
        if "Total Accesses:" in line:
            key = "exampleservice.apache.total.accesses"
            val  = {'val':int(line.strip("Total Accesses:")), 'unit':'accesses', 'metric_type':'gauge'}
        elif "Total kBytes:" in line:
            key = "exampleservice.apache.total.kBytes"
            val  = {'val':float(line.strip("Total kBytes:")), 'unit':'kBytes', 'metric_type':'gauge'}
        elif "Uptime:" in line:
            key = "exampleservice.apache.uptime"
            val  = {'val':int(line.strip("Uptime:")), 'unit':'seconds', 'metric_type':'gauge'}
        elif "ReqPerSec:" in line:
            key = "exampleservice.apache.reqpersec"
            val  = {'val':float(line.strip("ReqPerSec:")), 'unit':'rate', 'metric_type':'gauge'}
        elif "BytesPerSec:" in line:
            key = "exampleservice.apache.bytespersec"
            val  = {'val':float(line.strip("BytesPerSec:")), 'unit':'rate', 'metric_type':'gauge'}
        elif "BytesPerReq:" in line:
            key = "exampleservice.apache.bytesperreq"
            val  = {'val':float(line.strip("BytesPerReq:")), 'unit':'rate', 'metric_type':'gauge'}
        elif "BusyWorkers:" in line:
            key = "exampleservice.apache.busyworkers"
            val  = {'val':int(line.strip("BusyWorkers:")), 'unit':'workers', 'metric_type':'gauge'}
        elif "IdleWorkers:" in line:
            key = "exampleservice.apache.idleworkers"
            val  = {'val':int(line.strip("IdleWorkers:")), 'unit':'workers', 'metric_type':'gauge'}

        dictStatus[key] = val
        counter = counter + 1
        line = file.readline()

    return dictStatus

