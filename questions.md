1. How is vector serialized?  Answer:

Apparently uses the following implementation in fc/io/raw.hpp

template<typename Stream, typename T> inline void pack( Stream& s, const std::vector<T>& value )
template<typename Stream> inline void pack( Stream& s, const unsigned_int& v )

but I can't really find where this is "attached" to serialization.

2. Has anyone tried compiling on big-endian architecture?

3. Where is serialization of optional<whatever> implmented?

inline void pack( Stream& s, const fc::optional<T>& v )

which appears to output bool (one byte) followed by T.

4. Where is it specified that `enum chain_server_commands` will transmit on the wire as `uint64_t` ?  Or am I missing another 32-bit field?

5. Is `enum_chain_server_commands` 32-bit when the program is compiled on a 32-bit machine?  If so, this needs to be fixed, 32-bit chainserver
client should be able to communicate with a 64-bit chainserver and vice versa.

6. How does optional serialization deal with flag byte that is not 0 or 1?  We should add checks so other values of flag byte are reserved
and cause block to be rejected as malformed.



