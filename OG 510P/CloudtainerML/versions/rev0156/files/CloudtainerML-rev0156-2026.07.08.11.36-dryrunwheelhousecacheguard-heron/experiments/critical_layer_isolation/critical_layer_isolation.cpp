// CloudtainerML rev0026 — Critical Layer Isolation compression probe.
#include <bits/stdc++.h>
using namespace std; struct Row{string regime,method; double compression,score,loss,params,critical_miss,latency;};
static string esc(const string&s){string o;for(char c:s){if(c=='"'||c=='\\')o+='\\';o+=c;}return o;}
int main(){
 vector<string> regimes={"layer0_dominant","middle_layer_dominant","late_layer_dominant","uniform_depth","early_induction_head"};
 vector<string> methods={"uniform_bottleneck","protect_layer0_cli","protect_middle","protect_last","hpo_single_layer_protect","two_anchor_protect","uncompressed_oracle"};
 vector<double> comps={0.35,0.50,0.65,0.75}; vector<Row> rows; map<string,int>wins,nonoracle;
 for(auto&r:regimes) for(double c:comps){ vector<Row> cand; for(auto&m:methods){
   double params=1-c; if(m=="uncompressed_oracle") params=1.0;
   double protects0=(m=="protect_layer0_cli"||m=="hpo_single_layer_protect"||m=="two_anchor_protect"||m=="uncompressed_oracle");
   double protectsM=(m=="protect_middle"||m=="hpo_single_layer_protect"||m=="two_anchor_protect"||m=="uncompressed_oracle");
   double protectsL=(m=="protect_last"||m=="two_anchor_protect"||m=="uncompressed_oracle");
   double miss=0;
   if(r=="layer0_dominant"||r=="early_induction_head") miss += protects0?0:.70*c;
   if(r=="middle_layer_dominant") miss += protectsM?0:.62*c;
   if(r=="late_layer_dominant") miss += protectsL?0:.55*c;
   if(r=="uniform_depth") miss += .22*c - .06*(protects0+protectsM+protectsL);
   double overhead=(m=="hpo_single_layer_protect"?.05:m=="two_anchor_protect"?.09:0) + (m=="uncompressed_oracle"?.35:0);
   double bottleneck_loss = .18 + .42*c + miss;
   if(m=="uniform_bottleneck") bottleneck_loss += (r=="layer0_dominant"?.35*c:0);
   if(m=="uncompressed_oracle") bottleneck_loss = .10;
   double latency=.25 + .50*params + overhead;
   double score=bottleneck_loss + .22*latency + .14*params + .50*miss;
   cand.push_back({r,m,c,score,bottleneck_loss,params,miss,latency});
 }
 auto best=min_element(cand.begin(),cand.end(),[](auto&a,auto&b){return a.score<b.score;}); wins[best->method]++; if(best->method.find("oracle")==string::npos) nonoracle[best->method]++; rows.insert(rows.end(),cand.begin(),cand.end()); }
 cout << "{\n\"project\":\"CloudtainerML\",\n\"revision\":\"rev0026\",\n\"probe\":\"critical_layer_isolation\",\n\"summary\":{";
 cout << "\"row_count\":"<<rows.size()<<",\"primary_metric\":{\"name\":\"score\",\"direction\":\"lower_is_better\",\"winner_field\":\"method\"},";
 auto emit=[&](const map<string,int>&mp){cout<<"{";bool f=true;for(auto&kv:mp){if(!f)cout<<",";f=false;cout<<"\""<<esc(kv.first)<<"\":"<<kv.second;}cout<<"}";};
 cout<<"\"winner_counts\":";emit(wins);cout<<",\"nonoracle_winner_counts\":";emit(nonoracle);cout<<",\"interpretation\":\"Protecting layer 0 is excellent only in early-critical regimes; HPO/two-anchor policies are safer when the critical layer can move.\",\"tail_contract\":\"critical_miss records layer-specific failure rather than only average compression loss.\"},\n\"rows\":[\n";
 for(size_t i=0;i<rows.size();++i){auto&x=rows[i];if(i)cout<<",\n";cout<<"{\"regime\":\""<<x.regime<<"\",\"method\":\""<<x.method<<"\",\"compression\":"<<x.compression<<",\"score\":"<<x.score<<",\"loss_proxy\":"<<x.loss<<",\"params_fraction\":"<<x.params<<",\"critical_miss\":"<<x.critical_miss<<",\"latency_proxy\":"<<x.latency<<"}";} cout<<"\n]}\n";
}
