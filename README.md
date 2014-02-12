akri
====

Commands to ease riak interaction.
This started out as a document on common riak REST operations.
I got tired of copying and pasting, so I made commands out of them.

### keys

* streaming keys

        ./akri.py keys yoyo --host=127.0.0.1 | head -1000

* converting keys to values and pretty print

         ./akri.py keys my_bucket \
         | head -1000 \
         | ./akri.py vals my_bucket \
         | jq -M .


* deleting

        ./akri.py keys my_bucket \
        | grep deleteme \
        | ./akri.py delete my_bucket --dryrun=True

### bucket props

        ./akri.py bucket_props my_bucket \
        | jq -M -c '[.props.last_write_wins, .props.allow_mult]'

### conflict resolution policy

* query for it

        ./akri.py conflict_resolution_policy my_bucket --host=127.0.0.1
        http://127.0.0.1:8098/buckets/yoyo           most_recent        pick most recent sibling. 

* what are my options again?

       ./akri.py conflict_resolution_policy_doc
       policy          last_write_wins allow_mult      description
       siblings        False           True            let application handle siblings.
       most_recent     False           False           pick most recent sibling. default.
       stomp           True            False           just clobber.
       undefined       True            True            do not use.

* how do I set the conflict resolution policy?

       ./akri.py conflict_resolution_policy_update my_bucket most_recent

### todo

* key range
* enumerate buckets without walking the entire key space
* layered operation modes: output http request data, show equivalent curl command, actually do it.
