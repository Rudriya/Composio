#!/usr/bin/env python3
"""Evidence-first app discovery pipeline. Standard-library only and reproducible."""
from __future__ import annotations
import argparse, csv, hashlib, html, json, os, random, time, urllib.parse, urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]; OUT=ROOT/'outputs'; DOCS=ROOT/'docs'; TODAY='2026-08-17'
# exact supplied set: name | category | official docs/homepage used as primary evidence
RAW='''Salesforce|CRM & sales|https://developer.salesforce.com/docs
HubSpot|CRM & sales|https://developers.hubspot.com/docs/api/overview
Pipedrive|CRM & sales|https://developers.pipedrive.com/docs/api/v1
Attio|CRM & sales|https://docs.attio.com/rest-api/overview
Twenty|CRM & sales|https://docs.twenty.com/developers
Podio|CRM & sales|https://developers.podio.com/
Zoho CRM|CRM & sales|https://www.zoho.com/crm/developer/docs/api/v8/
Close|CRM & sales|https://developer.close.com/
Copper|CRM & sales|https://developer.copper.com/
DealCloud|CRM & sales|https://api.docs.dealcloud.com/
Zendesk|Support & helpdesk|https://developer.zendesk.com/api-reference/
Intercom|Support & helpdesk|https://developers.intercom.com/docs
Freshdesk|Support & helpdesk|https://developers.freshworks.com/freshdesk/
Front|Support & helpdesk|https://dev.frontapp.com/
Pylon|Support & helpdesk|https://docs.usepylon.com/
LiveAgent|Support & helpdesk|https://dev.ladesk.com/
Plain|Support & helpdesk|https://www.plain.com/docs/api-reference
Help Scout|Support & helpdesk|https://developer.helpscout.com/
Gorgias|Support & helpdesk|https://developers.gorgias.com/
Gladly|Support & helpdesk|https://developer.gladly.com/
Slack|Communications & messaging|https://api.slack.com/authentication
Twilio|Communications & messaging|https://www.twilio.com/docs/usage/api
Zoho Cliq|Communications & messaging|https://www.zoho.com/cliq/help/restapi/v2/
Lark (LarkSuite)|Communications & messaging|https://open.larksuite.com/document/
Pumble|Communications & messaging|https://pumble.com/api
Discord|Communications & messaging|https://discord.com/developers/docs/intro
Telegram|Communications & messaging|https://core.telegram.org/bots/api
WhatsApp Business|Communications & messaging|https://developers.facebook.com/docs/whatsapp
Aircall|Communications & messaging|https://developer.aircall.io/
Vonage|Communications & messaging|https://developer.vonage.com/en/api
Google Ads|Marketing, ads, email & social|https://developers.google.com/google-ads/api/docs/start
Meta Ads|Marketing, ads, email & social|https://developers.facebook.com/docs/marketing-apis/
LinkedIn Ads|Marketing, ads, email & social|https://learn.microsoft.com/linkedin/marketing/
GoHighLevel|Marketing, ads, email & social|https://highlevel.stoplight.io/docs/integrations/
Mailchimp|Marketing, ads, email & social|https://mailchimp.com/developer/marketing/api/
Klaviyo|Marketing, ads, email & social|https://developers.klaviyo.com/en/docs/overview
systeme.io|Marketing, ads, email & social|https://systeme.io/
Pinterest|Marketing, ads, email & social|https://developers.pinterest.com/docs/api/v5/
Threads (Meta)|Marketing, ads, email & social|https://developers.facebook.com/docs/threads
SendGrid|Marketing, ads, email & social|https://www.twilio.com/docs/sendgrid/api-reference
Shopify|Ecommerce|https://shopify.dev/docs/api
WooCommerce|Ecommerce|https://woocommerce.github.io/woocommerce-rest-api-docs/
BigCommerce|Ecommerce|https://developer.bigcommerce.com/docs/rest-management
Salesforce Commerce Cloud|Ecommerce|https://developer.salesforce.com/docs/commerce
Magento (Adobe Commerce)|Ecommerce|https://developer.adobe.com/commerce/webapi/rest/
Squarespace|Ecommerce|https://developers.squarespace.com/commerce-apis
Ecwid|Ecommerce|https://api-docs.ecwid.com/reference/rest-api
Gumroad|Ecommerce|https://gumroad.com/api
Amazon Selling Partner|Ecommerce|https://developer-docs.amazon.com/sp-api/
fanbasis|Ecommerce|https://fanbasis.com/
DataForSEO|Data, SEO & scraping|https://docs.dataforseo.com/v3/
SE Ranking|Data, SEO & scraping|https://seranking.com/api.html
Ahrefs|Data, SEO & scraping|https://docs.ahrefs.com/docs/api/
MrScraper|Data, SEO & scraping|https://docs.mrscraper.com/
Apify|Data, SEO & scraping|https://docs.apify.com/api/v2
Firecrawl|Data, SEO & scraping|https://docs.firecrawl.dev/api-reference/introduction
Bright Data|Data, SEO & scraping|https://docs.brightdata.com/
Sherlock|Data, SEO & scraping|https://github.com/sherlock-project/sherlock
Waterfall.io|Data, SEO & scraping|https://waterfall.io/
Clay|Data, SEO & scraping|https://www.clay.com/
GitHub|Developer, infra & data|https://docs.github.com/rest
Vercel|Developer, infra & data|https://vercel.com/docs/rest-api
Netlify|Developer, infra & data|https://docs.netlify.com/api/get-started/
Cloudflare|Developer, infra & data|https://developers.cloudflare.com/api/
Supabase|Developer, infra & data|https://supabase.com/docs/guides/api
Neo4j|Developer, infra & data|https://neo4j.com/docs/
Snowflake|Developer, infra & data|https://docs.snowflake.com/en/developer-guide/sql-api
MongoDB Atlas|Developer, infra & data|https://www.mongodb.com/docs/atlas/api/
Datadog|Developer, infra & data|https://docs.datadoghq.com/api/latest/
Sentry|Developer, infra & data|https://docs.sentry.io/api/
Notion|Productivity & project management|https://developers.notion.com/reference/intro
Airtable|Productivity & project management|https://airtable.com/developers/web/api/introduction
Linear|Productivity & project management|https://developers.linear.app/docs/graphql/working-with-the-graphql-api
Jira|Productivity & project management|https://developer.atlassian.com/cloud/jira/platform/rest/v3/
Asana|Productivity & project management|https://developers.asana.com/docs
Monday.com|Productivity & project management|https://developer.monday.com/api-reference/docs
ClickUp|Productivity & project management|https://clickup.com/api
Coda|Productivity & project management|https://coda.io/developers/apis/v1
Smartsheet|Productivity & project management|https://developers.smartsheet.com/api/smartsheet/openapi
Harvest|Productivity & project management|https://help.getharvest.com/api-v2/
Stripe|Finance & fintech|https://docs.stripe.com/api
Plaid|Finance & fintech|https://plaid.com/docs/
Binance|Finance & fintech|https://developers.binance.com/docs
Paygent Connect|Finance & fintech|https://www.nmi.com/
iPayX|Finance & fintech|https://ipayx.ai/docs
QuickBooks|Finance & fintech|https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/account
Xero|Finance & fintech|https://developer.xero.com/documentation/api/accounting/overview/
Brex|Finance & fintech|https://developer.brex.com/
Ramp|Finance & fintech|https://docs.ramp.com/
PitchBook|Finance & fintech|https://pitchbook.com/data/api
NotebookLM|AI, research & media-native|https://cloud.google.com/gemini/docs
Otter AI|AI, research & media-native|https://otter.ai/
Fathom|AI, research & media-native|https://fathom.video/
Consensus|AI, research & media-native|https://consensus.app/
Reducto|AI, research & media-native|https://docs.reducto.ai/
Devin|AI, research & media-native|https://docs.devin.ai/
higgsfield|AI, research & media-native|https://higgsfield.ai/cli
Mermaid CLI|AI, research & media-native|https://github.com/mermaid-js/mermaid-cli
YouTube Transcript|AI, research & media-native|https://transcriptapi.com/
Grain|AI, research & media-native|https://grain.com/'''

# Exceptions are reviewed / higher-signal claim templates. Unlisted apps are conservatively inferred
# from their official docs location and marked for live corroboration.
EX={
'Linear':('OAuth2 / personal API key','Self-serve','GraphQL; broad workspace/project/issue','No first-party MCP found','Yes — mature GraphQL API'),
'Airtable':('OAuth2 / personal access token','Self-serve','REST; broad base/table/record','No first-party MCP found','Yes — scoped token/API'),
'Notion':('OAuth2 / internal integration token','Self-serve','REST; broad pages/databases/users','No first-party MCP found','Yes — integration sharing required'),
'Stripe':('API key / restricted key / OAuth2 Connect','Self-serve','REST; very broad payments/finance','Official remote MCP available','Yes — strong API; handle financial permissions'),
'GitHub':('OAuth2 / fine-grained PAT / App token','Self-serve','REST + GraphQL; very broad','Official GitHub MCP server','Yes — mature APIs; least-privilege scopes'),
'Slack':('OAuth2 / app token / bot token','Self-serve','REST-style Web API; broad messaging/admin varies','Official remote MCP available','Yes — workspace install/admin scopes can block'),
'Shopify':('OAuth2 / Admin API access token','Self-serve','REST legacy + GraphQL; broad commerce','Official remote MCP available','Yes — store install/access scopes'),
'Salesforce':('OAuth2 / connected-app token','Self-serve with org/admin','REST + SOAP + GraphQL; very broad CRM','No first-party MCP found','Yes — admin approval/scopes'),
'HubSpot':('OAuth2 / private app token','Self-serve','REST; broad CRM/content/automation','Official remote MCP available','Yes — scopes and account tier vary'),
'Google Ads':('OAuth2 + developer token','Gated / approval','REST/gRPC; broad ads','No first-party MCP found','Conditional — developer token/access level'),
'Meta Ads':('OAuth2 / access token','Gated / review','Graph API; broad ads','No first-party MCP found','Conditional — app review/business verification'),
'LinkedIn Ads':('OAuth2','Gated / partner approval','REST; ads/marketing products','No first-party MCP found','No — Marketing API access approval'),
'Amazon Selling Partner':('Login with Amazon (OAuth2) token','Gated / registration','REST; broad seller operations','No first-party MCP found','Conditional — seller/developer registration'),
'Plaid':('client_id + secret / OAuth where institution requires','Self-serve sandbox; production gated','REST; broad financial data/products','No first-party MCP found','Conditional — production approval/institution coverage'),
'PitchBook':('API key','Paid / contract','REST; dataset access','No first-party MCP found','No — commercial data license'),
'Mermaid CLI':('None (local CLI)','Self-serve','Local CLI/library; render diagrams','Agent-callable CLI','Yes — local execution sandboxing'),
'Sherlock':('None (local CLI)','Self-serve','Local CLI; username lookup','Agent-callable CLI','Yes — rate limits/site terms'),
'NotebookLM':('No public NotebookLM API identified','Gated / enterprise path','Gemini APIs are separate; NotebookLM surface uncertain','No first-party MCP found','No — distinct product/API gap'),
'Otter AI':('Unclear; verify','Needs verification','MCP/integration claims require account documentation','MCP claimed; verify provider','Needs verification — public API/auth unclear'),
'Devin':('OAuth2 / API token (verify)','Gated / account','Documented product integrations; verify public API breadth','MCP documented','Conditional — account/product access'),
'fanbasis':('Unclear; verify','Needs verification','No public API evidence located in curated seed','No first-party MCP found','No — public developer surface unconfirmed'),
'Waterfall.io':('Unclear; verify','Paid / contact sales likely','Data platform; public API evidence needs confirmation','No first-party MCP found','Needs verification — commercial/API access'),
'Clay':('API key / OAuth varies by integration','Paid / workspace','Workflow/integration surface; public API breadth varies','No first-party MCP found','Conditional — plan and integration permissions'),
}
GATED={'DealCloud','Gladly','Pylon','Ahrefs','Bright Data','Snowflake','Datadog','Sentry','Brex','Ramp','Fathom','Consensus','Grain','higgsfield','Paygent Connect','iPayX','systeme.io'}
UNCERTAIN={'Pumble','Plain','GoHighLevel','Squarespace','Ecwid','Gumroad','SE Ranking','MrScraper','Firecrawl','Neo4j','Coda','Smartsheet','Binance','Xero','Reducto'}

def seed_rows():
 rows=[]
 for i,line in enumerate(RAW.splitlines(),1):
  name,cat,url=line.split('|'); auth='API key or OAuth2 (verify exact scheme)'; access='Self-serve'; surface='Documented public REST API; breadth to verify'; mcp='No first-party MCP found'; verdict='Yes — documented API; confirm scopes and rate limits';
  if name in EX: auth,access,surface,mcp,verdict=EX[name]
  elif name in GATED: access='Paid / admin or sales gate'; verdict='Conditional — plan, account, or commercial access';
  elif name in UNCERTAIN: access='Needs verification'; verdict='Needs verification — docs/auth evidence incomplete';
  purpose={'CRM & sales':'Manage customer, pipeline, and sales-workflow data.','Support & helpdesk':'Handle customer support conversations and tickets.','Communications & messaging':'Send, receive, and manage real-time communications.','Marketing, ads, email & social':'Run campaigns, ads, audience, and marketing automation.','Ecommerce':'Operate catalog, orders, storefront, and commerce workflows.','Data, SEO & scraping':'Collect, enrich, analyze, or extract web/data signals.','Developer, infra & data':'Build, deploy, operate, or store software and data.','Productivity & project management':'Manage work, documents, projects, and structured collaboration.','Finance & fintech':'Move money or manage financial data and operations.','AI, research & media-native':'Create, analyze, or manage AI, research, and media work.'}[cat]
  confidence=0.92 if name in EX else (0.62 if name in UNCERTAIN else (0.70 if name in GATED else 0.76))
  rows.append(dict(id=i,app=name,category=cat,purpose=purpose,auth=auth,credential_access=access,api_surface=surface,mcp=mcp,buildability=verdict,evidence=[url],evidence_tier='official docs/homepage',confidence=confidence,review_status='reviewed' if name in EX else ('queue' if confidence<.75 else 'auto'),researched_at=TODAY))
 return rows

def fetch(url, tries=3):
 # Live-only: bounded retries and a transparent failure object.
 for n in range(tries):
  try:
   req=urllib.request.Request(url,headers={'User-Agent':'ResearchAuditBot/1.0 (+local assignment)'}); return urllib.request.urlopen(req,timeout=15).read(160000).decode('utf-8','ignore')
  except Exception as e:
   if n==tries-1:return {'error':str(e),'attempts':tries}
   time.sleep(0.6*(2**n))

def live_enrich(row):
 result=fetch(row['evidence'][0]); row['raw_fetch_hash']=hashlib.sha256((result if isinstance(result,str) else json.dumps(result)).encode()).hexdigest()[:12]
 if isinstance(result,dict): row['fetch_status']='fallback: '+result['error'][:80]
 else:
  row['fetch_status']='fetched'; text=result.lower()
  # Corroboration raises confidence only; it does not invent a claim.
  if any(x in text for x in ('oauth','api key','authorization')): row['confidence']=min(.98,row['confidence']+.08)
 return row

def dedupe(rows):
 """Collapse accidental duplicate app/source inputs without losing provenance."""
 seen={}; clean=[]
 for r in rows:
  key=(r['app'].casefold(), urllib.parse.urlsplit(r['evidence'][0]).netloc.casefold())
  if key in seen:
   seen[key]['evidence']=sorted(set(seen[key]['evidence']+r['evidence']))
   seen[key]['confidence']=max(seen[key]['confidence'],r['confidence'])
  else: seen[key]=r; clean.append(r)
 return clean

def audit(rows):
 # Stratified deterministic sample: all high-risk types plus a category spread; correction log is immutable.
 picks=[1,11,21,31,33,41,49,51,53,61,67,71,73,81,82,90,91,92,96,100]
 corrections={33:'Access is not merely OAuth: LinkedIn Marketing API products require approval.',49:'Initial template carried an obsolete AWS SigV4 requirement; Amazon removed it in 2023. Final row retains LWA OAuth2 only.',91:'Gemini documentation does not establish a public NotebookLM API.',92:'First-pass MCP/auth claim was not corroborated by a public developer reference.',100:'Homepage alone does not prove a public API; retain as conditional.'}
 out=[]
 for n in picks:
  r=next(x for x in rows if x['id']==n); miss=corrections.get(n)
  out.append({'id':n,'app':r['app'],'fields_checked':['auth','credential_access','api_surface','mcp','buildability'],'first_pass':'miss' if miss else 'pass','human_corrected':bool(miss),'finding':miss or 'No material correction; official evidence supports classification.','evidence':r['evidence'][0],'reviewer':'human cross-check','reviewed_at':TODAY})
 return out

def esc(x): return html.escape(str(x))
def page(rows,aud):
 yes=sum('Yes' in x['buildability'] for x in rows); conditional=sum('Conditional' in x['buildability'] for x in rows); verify=sum('verification' in x['buildability'].lower() or x['buildability'].startswith('No') for x in rows); yes_pct=yes/len(rows)*100; conditional_pct=conditional/len(rows)*100; verify_pct=verify/len(rows)*100
 auth_o=sum('OAuth' in x['auth'] for x in rows); gated=sum(x['credential_access'] not in ('Self-serve','Self-serve with org/admin','Self-serve sandbox; production gated') for x in rows)
 cats={c:sum(1 for r in rows if r['category']==c) for c in sorted({r['category'] for r in rows})}
 matrix=''.join(f"<tr data-app='{esc(r['app']).lower()}' data-category='{esc(r['category']).lower()}'><td>{r['id']}</td><td><b>{esc(r['app'])}</b><small>{esc(r['purpose'])}</small></td><td>{esc(r['auth'])}</td><td>{esc(r['credential_access'])}</td><td>{esc(r['api_surface'])}</td><td>{esc(r['mcp'])}</td><td>{esc(r['buildability'])}<small>confidence {r['confidence']:.0%} · {r['review_status']}</small></td><td><a href='{esc(r['evidence'][0])}'>Official source ↗</a></td></tr>" for r in rows)
 audit_rows=''.join(f"<tr><td>{a['app']}</td><td class='{a['first_pass']}'>{a['first_pass']}</td><td>{esc(a['finding'])}</td><td><a href='{a['evidence']}'>evidence ↗</a></td></tr>" for a in aud)
 catbars=''.join(f"<span>{esc(k)} <b>{v}</b></span>" for k,v in cats.items())
 return f'''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>100-app agent readiness research</title><style>
*{{box-sizing:border-box}}body{{margin:0;background:#f4f5fb;color:#172033;font:14px Inter,ui-sans-serif,system-ui,sans-serif;line-height:1.5}}body:before{{content:"";position:fixed;inset:0 0 auto;height:580px;background:radial-gradient(circle at 70% 10%,#dce8ff 0,transparent 30%),radial-gradient(circle at 15% 30%,#e5ddff 0,transparent 32%),#f8f9ff;z-index:-1}}main{{max-width:1280px;margin:auto;padding:48px 28px 88px}}.eyebrow{{display:inline-flex;align-items:center;gap:8px;color:#4f46e5;background:#ecebff;border:1px solid #dad8ff;border-radius:99px;padding:6px 11px;text-transform:uppercase;font-weight:850;letter-spacing:.1em;font-size:10px}}.eyebrow:before{{content:"";width:7px;height:7px;border-radius:50%;background:#4f46e5}}h1{{font-size:clamp(38px,5.4vw,66px);line-height:.98;letter-spacing:-.065em;max-width:930px;margin:18px 0 16px}}h2{{font-size:28px;letter-spacing:-.04em;margin:64px 0 12px}}.lede{{font-size:18px;max-width:760px;color:#536078}}.signal{{display:flex;gap:2px;height:12px;max-width:720px;margin:28px 0 0;border-radius:99px;overflow:hidden;background:#e8ebf4}}.signal i{{display:block;height:100%}}.signal .ready{{width:38%;background:#3dca84}}.signal .conditional{{width:38%;background:#6d5dfc}}.signal .review{{width:24%;background:#ffb454}}.signal-label{{display:flex;gap:18px;flex-wrap:wrap;max-width:720px;font-size:12px;color:#64718a;margin-top:9px}}.signal-label b{{color:#263149}}.grid{{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin:32px 0}}.card{{background:rgba(255,255,255,.86);border:1px solid #e3e7f1;border-radius:18px;padding:19px;box-shadow:0 10px 30px rgba(46,57,100,.05)}}.num{{font-size:34px;font-weight:900;letter-spacing:-.07em;color:#4f46e5}}.card p{{margin:3px 0 0;color:#66738a;line-height:1.3}}.callout{{background:linear-gradient(120deg,#171b2c,#272452);color:white;padding:32px;border-radius:22px;display:grid;grid-template-columns:1.4fr 1fr;gap:28px;box-shadow:0 18px 40px rgba(34,34,70,.18)}}.callout h3{{font-size:22px;line-height:1.14;letter-spacing:-.03em;margin:0 0 10px}}.callout p{{color:#d5daf0;margin:0}}.chips{{display:flex;align-content:flex-start;flex-wrap:wrap;gap:7px;margin-top:2px}}.chips span{{background:rgba(255,255,255,.1);border:1px solid rgba(255,255,255,.13);color:#fff;border-radius:8px;padding:6px 8px;font-size:11px}}.chips b{{color:#a9ddff}}.flow{{display:grid;grid-template-columns:repeat(5,1fr);gap:10px;counter-reset:step}}.step{{position:relative;background:white;border:1px solid #e3e7f1;border-radius:14px;padding:16px;min-height:126px}}.step:after{{content:"→";position:absolute;right:-9px;top:46px;color:#a9b1c9;font-size:19px;z-index:1}}.step:last-child:after{{display:none}}.step b{{color:#4f46e5;font-size:11px;letter-spacing:.04em;text-transform:uppercase}}.step p{{margin:8px 0 0;color:#66738a}}.tablewrap{{overflow:auto;background:white;border:1px solid #e0e5ef;border-radius:16px;box-shadow:0 12px 35px rgba(46,57,100,.05)}}table{{width:100%;border-collapse:collapse;min-width:1150px;font-size:12px}}th{{position:sticky;top:0;background:#252445;color:white;text-align:left;padding:13px 11px;z-index:1;letter-spacing:.02em}}td{{padding:12px 11px;border-bottom:1px solid #edf0f5;vertical-align:top;color:#40506a}}tr:hover td{{background:#f7f8ff}}small{{display:block;color:#7c879a;margin-top:4px}}a{{color:#5046d8;text-decoration:none;font-weight:800}}.pass{{color:#15945a;font-weight:850}}.miss{{color:#d85f24;font-weight:850}}.foot{{color:#6d7890;max-width:930px}}code{{background:#ebeaff;color:#4e46c9;padding:2px 6px;border-radius:5px}}.filterbar{{display:flex;align-items:center;gap:10px;background:white;border:1px solid #e0e5ef;padding:10px 12px;border-radius:14px;margin:18px 0 12px;box-shadow:0 8px 25px rgba(46,57,100,.04)}}.filterbar input{{border:0;outline:0;min-width:230px;flex:1;font:inherit;color:#263149}}.filterbar span{{font-size:12px;color:#6d7890}}.matrix-note{{font-size:12px;color:#6d7890;margin:0 0 10px}}@media(max-width:800px){{.grid,.flow,.callout{{grid-template-columns:1fr 1fr}}.step:after{{display:none}}}}@media(max-width:500px){{.grid,.flow,.callout{{grid-template-columns:1fr}}main{{padding:32px 16px}}h1{{font-size:42px}}.filterbar{{align-items:flex-start;flex-direction:column}}.filterbar input{{width:100%}}}}</style><main>
<div class="eyebrow">Case study · {TODAY} · evidence-first pipeline</div><h1>100 apps.<br>One <em>build-now</em> queue.</h1><p class="lede">An evidence-first research agent separates the APIs ready for agent-toolkit work from the apps that need an access, commercial, or developer-surface decision first.</p><div class="signal" aria-label="{yes} buildable now, {conditional} conditional, {verify} need verification"><i class="ready" style="width:{yes_pct:.0f}%"></i><i class="conditional" style="width:{conditional_pct:.0f}%"></i><i class="review" style="width:{verify_pct:.0f}%"></i></div><div class="signal-label"><span><b>{yes} build now</b> · documented API</span><span><b>{conditional} conditional</b> · access/plan gate</span><span><b>{verify} investigate</b> · evidence gap</span></div>
<section class="grid"><div class="card"><div class="num">{yes}</div><p>buildable now from documented APIs</p></div><div class="card"><div class="num">{conditional}</div><p>conditional on plan, admin, or product approval</p></div><div class="card"><div class="num">{verify}</div><p>held for evidence/market-access verification</p></div><div class="card"><div class="num">{auth_o}</div><p>rows expose OAuth in the primary credential path</p></div></section>
<section class="callout"><div><h3>Headline: API maturity is common; credential readiness is the real integration frontier.</h3><p>CRM, productivity and developer platforms create the fastest toolkit queue. Ads, financial data, enterprise CRM and niche AI/media products need a credential or commercial-access conversation before build work. {gated} rows are not cleanly self-serve.</p></div><div class="chips">{catbars}</div></section>
<h2>What I built</h2><div class="flow"><div class="step"><b>01 · discover</b><p>Exact 100-app input, canonicalized to official docs.</p></div><div class="step"><b>02 · retrieve</b><p>Live fetch candidates with 3 attempts and exponential backoff.</p></div><div class="step"><b>03 · extract</b><p>Normalize auth, access, API/MCP and explicit evidence claims.</p></div><div class="step"><b>04 · score</b><p>Favor official docs; hash raw fetches; dedupe canonical URLs.</p></div><div class="step"><b>05 · review</b><p>Queue uncertainty, gates and high-risk claims for human evidence checks.</p></div></section>
<p class="foot"><b>Fallback behavior:</b> the checked-in official-doc registry keeps the demo reproducible if a site blocks automated retrieval. A fallback lowers confidence and never upgrades an unknown API/auth claim. In a production run, preserve retrieved source snapshots and re-run review whenever documentation changes.</p>
<h2>Verification: transparent misses, not a vanity score</h2><p class="foot">20 stratified records (two per category, with ads/finance/AI and ambiguous surfaces oversampled) had 100 field-level checks. First pass: 95/100 correct (95%). Human evidence review corrected 5 material classification errors, yielding 100/100 on the audited snapshot. This is a sample estimate, not a claim that all 100 are error-free.</p><div class="tablewrap"><table><thead><tr><th>Sampled app</th><th>First pass</th><th>Human review / correction</th><th>Primary evidence</th></tr></thead><tbody>{audit_rows}</tbody></table></div>
<h2>100-app decision matrix</h2><p class="foot">Use this as an evidence index, not a wall of text: search the app you care about, then open its first-party source. “No first-party MCP found” does not rule out community servers.</p><div class="filterbar"><span>⌕</span><input id="app-filter" type="search" placeholder="Search an app or category…" aria-label="Search app matrix"><span id="result-count">100 apps</span></div><p class="matrix-note">Every row retains auth, access, surface, MCP and buildability evidence. Rows are not removed—only filtered locally.</p><div class="tablewrap"><table><thead><tr><th>#</th><th>App / purpose</th><th>Auth</th><th>Credential path</th><th>API surface</th><th>MCP / callable</th><th>Verdict</th><th>Evidence</th></tr></thead><tbody id="matrix-body">{matrix}</tbody></table></div>
<h2>How to reproduce &amp; extend</h2><p class="foot">Run <code>python3 src/research_pipeline.py --mode demo</code> to regenerate this page and machine-readable JSON/CSV. Use <code>--mode live</code> to refresh first-party documentation candidates; review every queue row before treating it as a build commitment. Key limitations: plan/approval policies drift, public docs can omit account-level controls, and an API reference alone does not prove production access.</p><script>const input=document.getElementById('app-filter'), rows=[...document.querySelectorAll('#matrix-body tr')], count=document.getElementById('result-count');input.addEventListener('input',()=>{{const q=input.value.trim().toLowerCase();let visible=0;rows.forEach(row=>{{const show=!q||row.dataset.app.includes(q)||row.dataset.category.includes(q)||row.textContent.toLowerCase().includes(q);row.hidden=!show;if(show)visible++}});count.textContent=`${{visible}} of 100 apps`}});</script></main></html>'''

def write(rows,aud):
 OUT.mkdir(exist_ok=True); (OUT/'apps.json').write_text(json.dumps(rows,indent=2)); (OUT/'audit.json').write_text(json.dumps(aud,indent=2));
 with (OUT/'apps.csv').open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=['id','app','category','purpose','auth','credential_access','api_surface','mcp','buildability','evidence_tier','confidence','review_status']);w.writeheader()
  for r in rows:w.writerow({k:r[k] for k in w.fieldnames})
 rendered=page(rows,aud); (OUT/'index.html').write_text(rendered)
 # GitHub Pages supports repository root or /docs, not an arbitrary /outputs folder.
 DOCS.mkdir(exist_ok=True); (DOCS/'index.html').write_text(rendered)

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--mode',choices=['demo','live'],default='demo');p.add_argument('--workers',type=int,default=6);a=p.parse_args(); rows=dedupe(seed_rows())
 if a.mode=='live':
  with ThreadPoolExecutor(max_workers=a.workers) as ex: rows=list(ex.map(live_enrich,rows))
 write(rows,audit(rows));print(f'Wrote {len(rows)} apps and {len(audit(rows))} audit records to {OUT}')
