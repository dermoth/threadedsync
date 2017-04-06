ThreadedSync
============

ThreadedSync is a script I wrote to copy many files dropped into one folder
over to a remote rsync endpoint. The code has been distributed mainly as a
threading + subprocesses example but is fully functional and has served
production use during a datacenter migration.

The goal was to rsync many files in parallel to fully use the large bandwidth
available between two distant datacenters.

The process should be set up as follow:

1. On the "local" side (which can also be an NFS or CIFS mount): processes
   should write or copy files to a temporary space then move them into the
   "tosync" folder. This is done so the move is atomic, otherwise we could
   rsync partial files.

2. threadedsync.py picks up files in the "tosync" folder, syncs them, then
   moves them into the "synced" folder. This can be used to monitor copy
   completion.

3. On the remote end, rsync will sync to temporary files and only after that
   rename them to the final file name, therefore any job loading those files
   should ignore rsync temp files.

You will need to adjust the paths and ssh key if you need one (see the rsync
command).

