
About
-----

This is my (drltc's) raw notes from going through the code.

None of this necessarily makes any sense to anyone but me.

But there might be some useful information in here, so I'm adding it.

Donation addresses
------------------

- Bitcoin: 1NfGejohzoVGffAD1CnCRgo9vApjCU2viY
- Litecoin: LiUGs9sqH6GBHsvzpNtLCoyXB5aCDi9HsQ
- Dogecoin: DTy5q7uUQ1whqyUrwC1LbhgqwKgovJT5R7
- Protoshares (BitShares-PTS): PZxpdC8RqWsdU3pVJeobZY7JFKVPfNpy5z
- BTSX: drltc

Notes
-----

Packed unsigned integers are in little endian order, 7 bits each, high bit set on all except last byte.

Proxy chain server with HTTP, then start another instance and download chain.

    sudo -u btsxt -H mkdir -p ~btsxt/BitSharesDownloadTest
    sudo -u btsxt -H cat ~btsxt/.BitSharesXTS-Test19/config.json | sed -e 's/"chain_servers": \[\]/"chain_servers": \["127.0.0.1:11230"\]/' | sudo -u btsxt -H sh -c 'cat >~btsxt/BitSharesDownloadTest/config.json'

    sudo -u btsxt -H sh -c 'socat -x tcp-listen:11230,reuseaddr tcp:127.0.0.1:11235 2> ~btsxt/BitSharesDownloadTest/socket.out' &
    sudo -u btsxt -H programs/client/bitshares_client --p2p-port 11234 --chain-server-port 11235 --disable-default-peers
    sudo -u btsxt -H programs/client/bitshares_client --p2p-port 11236 --resync-blockchain --disable-default-peers --data-dir ~btsxt/BitSharesDownloadTest

Here is what the conversation looks like:

    server: (uint32_t) PROTOCOL_VERSION
    client: (enum chain_server_commands) COMMAND

Apparently `enum_chain_server_commands` is `uint64_t`.  Where

When COMMAND is...
    finish = 0

we see the server does this:

    server: (close connection)

When COMMAND is...
    get_blocks_from_number = 1

We see the following conversation:
    client: (uint32_t) start_block

    while(server has more blocks):
        server: (uint32_t) blocks_to_send
        for each block:
            server: (full_block) blocks

        server: (uint32_t) 0

Here is my rough notes of the formats of everything:

   full_block : block_header delegate_signature user_transaction_ids signed_transactions

   typedef vector<signed_transaction> signed_transactions;
   typedef fc::ripemd160 block_id_type;
   typedef fc::sha256 digest_type;
   typedef fc::ripemd160 secret_hash_type;

   struct full_block
   {
       // block_header
       block_id_type        previous;
       uint32_t             block_num;
       fc::time_point_sec   timestamp;                  // uint32_t
       digest_type          transaction_digest;
       secret_hash_type     next_secret_hash;
       secret_hash_type     previous_secret;

       // delegate_signature
       signature_type delegate_signature;

       // user_transaction_ids
       signed_transactions  user_transactions;
   };

   struct signed_transaction
   {
      // transaction
      fc::time_point_sec          expiration;
      optional<slate_id_type>     delegate_slate_id; // delegate being voted for in required payouts
      vector<operation>           operations; 

      // signed_transaction
      vector<fc::ecc::compact_signature> signatures;
   };

   enum operation_type_enum
   {
      null_op_type                = 0,

      /** balance operations */
      withdraw_op_type            = 1,
      deposit_op_type             = 2,

      /** account operations */
      register_account_op_type    = 3,
      update_account_op_type      = 4,
      withdraw_pay_op_type        = 5,

      /** asset operations */
      create_asset_op_type        = 6,
      update_asset_op_type        = 7,
      issue_asset_op_type         = 8,

      /** delegate operations */
      fire_delegate_op_type       = 9,

      /** proposal operations */
      submit_proposal_op_type     = 10,
      vote_proposal_op_type       = 11,

      /** market operations */
      bid_op_type                 = 12,
      ask_op_type                 = 13,
      short_op_type               = 14,
      cover_op_type               = 15,
      add_collateral_op_type      = 16,
      remove_collateral_op_type   = 17,

      define_delegate_slate_op_type = 18,

      update_feed_op_type          = 19
   };

   /**
    *  A poly-morphic operator that modifies the blockchain database
    *  is some manner.
    */
   struct operation
   {
      fc::enum_type<uint8_t,operation_type_enum> type;
      std::vector<char> data;
   };


   void signed_transaction::sign( const fc::ecc::private_key& signer, const digest_type& chain_id )
   {
      signatures.push_back( signer.sign_compact( digest(chain_id) ) );
   }

   void transaction::define_delegate_slate( delegate_slate s )
   {
      FC_ASSERT( s.supported_delegates.size() > 0 )
      operations.emplace_back( define_delegate_slate_operation( std::move(s) ) );
   }

    start_block = max(start_block, 1);

    typedef fc::array<unsigned char,65> compact_signature;
    typedef fc::ecc::compact_signature signature_type;

    typedef uint64_t slate_id_type;


    optional:  8 byte aligned, plus bool valid.

Vectors of things are sent by packed integer length, followed by data.
Optional things are sent by a single flag byte indicating true/false, followed by data if flag byte was true.

Where is the size of COMMAND specified?  Does network protocol become incompatible when compiled as 32 bits?

Server sends PROTOCOL_VERSION (uint32_t)
Currently 0

