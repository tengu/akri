
all:

host=127.0.0.1
bucket=yoyo

conflict_resolution_policy_doc:
	./akri.py conflict_resolution_policy_doc

conflict_resolution_policy:
	./akri.py conflict_resolution_policy $(bucket) --host=$(host)

conflict_resolution_policy_update:
	./akri.py conflict_resolution_policy_update $(bucket) most_recent --host=$(host) --verbose

keys:
	./akri.py keys $(bucket) --host=$(host)

vals:
	./akri.py keys $(bucket) --host=$(host) \
	| ./akri.py vals $(bucket) --host=$(host) \
	| jq -M .

delete:
	./akri.py keys $(bucket) --host=$(host) \
	| ./akri.py delete $(bucket) --host=$(host) --dryrun=True

bucket_props:
	./akri.py bucket_props $(bucket) --host=$(host) \
	| jq -M -c '[.props.last_write_wins, .props.allow_mult]'
