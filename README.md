**>>WARNNING ON SCAMS IN ISSUES COMMENT SECTION<<**

The issues comment section is often targeted by scam bots willing to redirect you to an external resource and drain your funds.

I have enabled a GitHub actions script to detect the common patterns and tag them, which obviously is not 100% accurate.

This is also why you will see deleted comments in the issues—I only delete the scam bot comments targeting your private keys.

The official maintainers are in the [MAINTAINERS.md](MAINTAINERS.md) file.

Not everyone is a scammer though, sometimes there are helpful outside devs who comment and I absolutely appreciate it.

**>>END OF WARNING<<**

For the full walkthrough, see [Solana: Creating a trading and sniping pump.fun bot](https://docs.chainstack.com/docs/solana-creating-a-pumpfun-bot).

For near-instantaneous transaction propagation, you can use the [Chainstack Solana Trader nodes](https://docs.chainstack.com/docs/trader-nodes).

[Sign up with Chainstack](https://console.chainstack.com).

Make sure you have the required packages installed `pip install -r requirements.txt`.

Make sure you have your endpoints set up in `config.py`.

## Note on limits

Solana is an amazing piece of web3 architecture, but it's also very complex to maintain.

Chainstack is daily (literally, including weekends) working on optimizing our Solana infrastructure to make it the best in the industry.

That said, all node providers have their own setup recommendations & limits, like method availability, requests per second (RPS), free and paid plan specific limitations and so on.

So please make sure you consult the docs of the node provider you are going to use for the bot here. And obviously the public RPC nodes won't work for the heavier use case scenarios like this bot.

For Chainstack, all of the details and limits you need to be aware of are consolidated here: [Limits](https://docs.chainstack.com/docs/limits) <— we are _always_ keeping this piece up to date so you can rely on it.

## Changelog

Quick note on a couple on a few new scripts in `/learning-examples`:

*(this is basically a changelog now)*

Also, here's a quick doc: [Listening to pump.fun migrations to Raydium](https://docs.chainstack.com/docs/solana-listening-to-pumpfun-migrations-to-raydium)

## Bonding curve state check

`check_boding_curve_status.py` — checks the state of the bonding curve associated with a token. When the bonding curve state is completed, the token is migrated to Raydium.

To run:

`python check_boding_curve_status.py TOKEN_ADDRESS`

## Listening to the Raydium migration

When the bonding curve state completes, the liquidity and the token graduate to Raydium.

`listen_to_raydium_migration.py` — listens to the migration events of the tokens from pump_fun to Raydium and prints the signature of the migration, the token address, and the liquidity pool address on Raydium.

Note that it's using the [blockSubscribe]([url](https://docs.chainstack.com/reference/blocksubscribe-solana)) method that not all providers support, but Chainstack does and I (although obviously biased) found it pretty reliable.

To run:

`python listen_to_raydium_migration.py`

**The following two new additions are based on this question [associatedBondingCurve #26](https://github.com/chainstacklabs/pump-fun-bot/issues/26)**

You can take the compute the associatedBondingCurve address following the [Solana docs PDA](https://solana.com/docs/core/pda) description logic. Take the following as input *as seed* (order seems to matter):

- bondingCurve address
- the Solana system token program address: `TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA`
- the token mint address

And compute against the Solana system associated token account program address: `ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL`.

The implications of this are kinda huge:
* you can now use `logsSubscribe` to snipe the tokens and you are not limited to the `blockSubscribe` method
* see which one is faster
* not every provider supports `blockSubscribe` on lower tier plans or at all, but everyone supports `logsSubscribe`

The following script showcase the implementation.

## Compute associated bonding curve

`compute_associated_bonding_curve.py` — computes the associated bonding curve for a given token.    

To run:

`python compute_associated_bonding_curve.py` and then enter the token mint address.

## Listen to new direct full details

`listen_new_direct_full_details.py` — listens to the new direct full details events and prints the signature, the token address, the user, the bonding curve address, and the associated bonding curve address using just the `logsSubscribe` method. Basically everything you need for sniping using just `logsSubscribe` and no extra calls like doing `getTransaction` to get the missing data. It's just computed on the fly now.

To run:

`python listen_new_direct_full_details.py`

So now you can run `listen_create_from_blocksubscribe.py` and `listen_new_direct_full_details.py` at the same time and see which one is faster.
