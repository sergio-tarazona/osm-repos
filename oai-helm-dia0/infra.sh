# Add PDU, replace "etsi-openstack" for the name of the VIM you're using
VIMID=`osm vim-list | grep "etsi-openstack " | awk '{ print $4 }'`
sed -i "s/vim_accounts: .*/vim_accounts: [ $VIMID ]/" pdu.yaml
osm pdu-create --descriptor_file pdu.yaml
