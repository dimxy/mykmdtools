#!/bin/bash
# compact notary wallet:
# first send all amount to self to spend old utxos
# then clean wallet's transactions

function compact_wallet() {
  CHAIN=$1
  ARGS=""
  echo chain=$CHAIN

  # echo "${chain}: lockunspent and sendtoaddress..."
  if [[ $CHAIN != "KMD" ]]; then
    ARGS="-ac_name=$CHAIN"
  fi

  { IFS= read TXCOUNT; } <<< "$(komodo-cli $ARGS getwalletinfo | jq .txcount)" 
  if [[ $TXCOUNT -gt 300 ]]; then  # compact only if tx count > 300

    { IFS= read ADDR; read AMOUNT; } <<< "$(komodo-cli $ARGS listaddressgroupings | jq -c --raw-output '.[0][0][0,1]')"

    # if address parsed okay:
    if [[ $ADDR = R* ]]; then
        komodo-cli $ARGS lockunspent true $(komodo-cli listlockunspent | jq -c .)
        echo chain ${CHAIN} txcount=${TXCOUNT} sending to self ${ADDR} ${AMOUNT}:
        komodo-cli $ARGS sendtoaddress $ADDR $AMOUNT \"\" \"\" true
        komodo-cli $ARGS cleanwallettransactions
    else 
        echo could not check komodo address=$ADDR
    fi
  fi
}

compact_wallet "KMD"
ASSETNAMES="BET BOTS CCL CLC CRYPTO DEX GLEEC HODL ILN JUMBLR JUMBLR KOIN MGW MORTY MSHARK MSHARK NINJA PANGEA PIRATE REVS RICK SUPERNET THC"
# ASSETNAMES="MCL TOKEL"

{ IFS=' ' read -a CHAINS; } <<< ${ASSETNAMES}
for CHAIN in "${CHAINS[@]}"; do
  compact_wallet $CHAIN
done
