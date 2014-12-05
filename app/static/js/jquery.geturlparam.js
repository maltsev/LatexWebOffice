/* Copyright (c) 2006-2007 Mathias Bank (http://www.mathias-bank.de)
 * Dual licensed under the MIT (http://www.opensource.org/licenses/mit-license.php) 
 * and GPL (http://www.opensource.org/licenses/gpl-license.php) licenses.
 * 
 * Version 2.1
 * 
 * Thanks to 
 * Hinnerk Ruemenapf - http://hinnerk.ruemenapf.de/ for bug reporting and fixing.
 * Tom Leonard for some improvements
 * 
 */
jQuery.fn.extend({getUrlParam:function(d){d=escape(unescape(d));var c=[],b=null;if("#document"==$(this).attr("nodeName"))-1<window.location.search.search(d)&&(b=window.location.search.substr(1,window.location.search.length).split("&"));else if("undefined"!=$(this).attr("src")){var a=$(this).attr("src");-1<a.indexOf("?")&&(b=a.substr(a.indexOf("?")+1),b=b.split("&"))}else if("undefined"!=$(this).attr("href"))a=$(this).attr("href"),-1<a.indexOf("?")&&(b=a.substr(a.indexOf("?")+1),b=b.split("&"));else return null;
if(null==b)return null;for(a=0;a<b.length;a++)escape(unescape(b[a].split("=")[0]))==d&&c.push(b[a].split("=")[1]);return 0==c.length?null:1==c.length?c[0]:c}});
