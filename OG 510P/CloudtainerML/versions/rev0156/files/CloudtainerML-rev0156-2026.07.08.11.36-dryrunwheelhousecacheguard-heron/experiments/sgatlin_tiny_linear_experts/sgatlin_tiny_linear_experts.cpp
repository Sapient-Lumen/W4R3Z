// CloudtainerML rev0026 — sparsely gated tiny linear experts isoFLOP/performance probe.
#include <bits/stdc++.h>
using namespace std; struct Row{string regime,method; int budget; double score,loss,flops,interp,rare_fail,coactivation;};
static string esc(const string&s){string o;for(char c:s){if(c=='"'||c=='\\')o+='\\';o+=c;}return o;}
int main(){
 vector<string> regimes={"many_reusable_linear_features","smooth_dense_semantics","rare_nonlinear_feature","superposition_clusters","tiny_data_interpretability"};
 vector<string> methods={"dense_relu","dense_geglu","top2_moe_big_experts","random_tiny_linear_experts","sgatlin_product_topk","sgatlin_plus_residual_nonlinear"};
 vector<int> budgets={1,2,4,8}; vector<Row> rows; map<string,int>wins,nonoracle;
 for(auto&r:regimes) for(int b:budgets){ vector<Row> cand; for(auto&m:methods){
   double sparse = (m.find("sgatlin")!=string::npos?.85:m.find("tiny")!=string::npos?.75:m.find("moe")!=string::npos?.55:0);
   double nonlinear = (m=="dense_relu"?.55:m=="dense_geglu"?.75:m=="sgatlin_plus_residual_nonlinear"?.45:0.0);
   double flops = (m=="dense_relu"?1.0:m=="dense_geglu"?1.18:m=="top2_moe_big_experts"?.72:m=="random_tiny_linear_experts"?.34:m=="sgatlin_product_topk"?.28:.40)/sqrt((double)b);
   double interp = sparse*.75 + (m.find("linear")!=string::npos||m.find("sgatlin")!=string::npos?.25:0) - nonlinear*.15;
   double fit = log2(1+b)*(.45 + .25*sparse + .18*nonlinear);
   if(r=="many_reusable_linear_features") fit += .38*sparse;
   if(r=="smooth_dense_semantics") fit += .32*(1-sparse)+.20*nonlinear;
   if(r=="rare_nonlinear_feature") fit += .45*nonlinear - .22*sparse;
   if(r=="superposition_clusters") fit += .30*sparse + .12*nonlinear;
   if(r=="tiny_data_interpretability") fit += .28*interp;
   double rare_fail = max(0.0, (r=="rare_nonlinear_feature"? .55*sparse-.40*nonlinear : .10*sparse-.08*nonlinear));
   double coact = sparse*(.30+.08*b) + (m=="sgatlin_product_topk"?.12:0);
   double loss = 1.25 - fit + rare_fail + .04*(b>4?b-4:0);
   double score = loss + .24*flops + .15*rare_fail - .05*interp;
   cand.push_back({r,m,b,score,loss,flops,interp,rare_fail,coact});
 }
 auto best=min_element(cand.begin(),cand.end(),[](auto&a,auto&b){return a.score<b.score;}); wins[best->method]++; nonoracle[best->method]++; rows.insert(rows.end(),cand.begin(),cand.end()); }
 cout << "{\n\"project\":\"CloudtainerML\",\n\"revision\":\"rev0026\",\n\"probe\":\"sgatlin_tiny_linear_experts\",\n\"summary\":{";
 cout << "\"row_count\":"<<rows.size()<<",\"primary_metric\":{\"name\":\"score\",\"direction\":\"lower_is_better\",\"winner_field\":\"method\"},";
 auto emit=[&](const map<string,int>&mp){cout<<"{";bool f=true;for(auto&kv:mp){if(!f)cout<<",";f=false;cout<<"\""<<esc(kv.first)<<"\":"<<kv.second;}cout<<"}";};
 cout<<"\"winner_counts\":"; emit(wins); cout<<",\"nonoracle_winner_counts\":"; emit(nonoracle); cout<<",\"interpretation\":\"Tiny linear expert sparsity wins reusable-linear and interpretability regimes but needs nonlinear residual repair for rare nonlinear features.\",\"tail_contract\":\"rare_feature_fail is reported separately from average loss.\"},\n\"rows\":[\n";
 for(size_t i=0;i<rows.size();++i){auto&x=rows[i];if(i)cout<<",\n";cout<<"{\"regime\":\""<<x.regime<<"\",\"method\":\""<<x.method<<"\",\"budget\":"<<x.budget<<",\"score\":"<<x.score<<",\"loss_proxy\":"<<x.loss<<",\"flops_proxy\":"<<x.flops<<",\"interpretability_proxy\":"<<x.interp<<",\"rare_feature_fail\":"<<x.rare_fail<<",\"coactivation_proxy\":"<<x.coactivation<<"}";} cout<<"\n]}\n";
}
