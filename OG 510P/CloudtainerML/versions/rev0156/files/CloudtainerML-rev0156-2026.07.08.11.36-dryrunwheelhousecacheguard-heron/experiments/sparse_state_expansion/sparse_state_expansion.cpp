// CloudtainerML rev0026 — Sparse State Expansion / row-sparse linear-attention state probe.
#include <bits/stdc++.h>
using namespace std; struct Row{string regime,method; int state; double score,error,bytes,interference,recall,latency;};
static string esc(const string&s){string o;for(char c:s){if(c=='"'||c=='\\')o+='\\';o+=c;}return o;}
int main(){
 vector<string> regimes={"associative_recall","key_collision_recall","smooth_prefix_lm","multi_hop_retrieval","arithmetic_reasoning"};
 vector<string> methods={"full_attention_oracle","local_window","linear_single_state","row_sparse_update","sse_4part","sse_8part","hybrid_sse_attention"};
 vector<int> states={16,32,64,128}; vector<Row> rows; map<string,int>wins,nonoracle;
 for(auto&r:regimes) for(int s:states){ vector<Row> cand; for(auto&m:methods){
   double parts = (m=="sse_4part"?4:m=="sse_8part"?8:m=="hybrid_sse_attention"?6:1);
   double sparse = (m=="row_sparse_update"?.45:m.find("sse")!=string::npos?.70:0);
   double attn = (m=="full_attention_oracle"?1.0:m=="hybrid_sse_attention"?.30:m=="local_window"?.12:0);
   double bytes = (m=="full_attention_oracle"?8.0:s/16.0*(1+.10*parts)+attn*4.0);
   double base = r=="smooth_prefix_lm"?.55:r=="arithmetic_reasoning"?.80:1.0;
   double capacity = log2(s+1)/7.0 + .18*log2(parts+1) + .25*attn;
   double interference = max(0.0, base - capacity - .16*sparse + (r=="key_collision_recall"?.22*(parts<4):0));
   double recall = max(0.0, min(1.0, capacity + .20*sparse + (r=="smooth_prefix_lm"?.18:0) - .12*interference));
   double error = .08 + .95*interference + (r=="multi_hop_retrieval" && attn<.2 ? .16:0) + (r=="arithmetic_reasoning" && sparse>.6 ? .06:0);
   double latency = .25 + .025*bytes + (m=="full_attention_oracle"?.55:0) + (m=="hybrid_sse_attention"?.16:0);
   double score = error + .20*latency + .05*bytes - .06*recall;
   cand.push_back({r,m,s,score,error,bytes,interference,recall,latency});
 }
 auto best=min_element(cand.begin(),cand.end(),[](auto&a,auto&b){return a.score<b.score;}); wins[best->method]++; if(best->method.find("oracle")==string::npos) nonoracle[best->method]++; rows.insert(rows.end(),cand.begin(),cand.end()); }
 cout << "{\n\"project\":\"CloudtainerML\",\n\"revision\":\"rev0026\",\n\"probe\":\"sparse_state_expansion\",\n\"summary\":{";
 cout << "\"row_count\":"<<rows.size()<<",\"primary_metric\":{\"name\":\"score\",\"direction\":\"lower_is_better\",\"winner_field\":\"method\"},";
 auto emit=[&](const map<string,int>&mp){cout<<"{";bool f=true;for(auto&kv:mp){if(!f)cout<<",";f=false;cout<<"\""<<esc(kv.first)<<"\":"<<kv.second;}cout<<"}";};
 cout<<"\"winner_counts\":";emit(wins);cout<<",\"nonoracle_winner_counts\":";emit(nonoracle);cout<<",\"interpretation\":\"Sparse state expansion helps when interference/class collision is the bottleneck, but hybrid attention remains useful for multi-hop regimes.\",\"tail_contract\":\"interference_error is separate from average state bytes.\"},\n\"rows\":[\n";
 for(size_t i=0;i<rows.size();++i){auto&x=rows[i];if(i)cout<<",\n";cout<<"{\"regime\":\""<<x.regime<<"\",\"method\":\""<<x.method<<"\",\"state_size\":"<<x.state<<",\"score\":"<<x.score<<",\"error\":"<<x.error<<",\"state_bytes_proxy\":"<<x.bytes<<",\"interference_error\":"<<x.interference<<",\"recall_proxy\":"<<x.recall<<",\"latency_proxy\":"<<x.latency<<"}";} cout<<"\n]}\n";
}
