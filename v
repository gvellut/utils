#!/usr/bin/perl
$pid = 0;
open I, "ps -axww -U $ENV{'USER'} |";
while (<I>)
{
    if (/MacVim/ && !/grep/)
 	{
 	    if (/^\s*([0-9]+)\s/)
 		{
 		    $pid = $1;
 		    }
 	}
 }
 
close I;
$args = "";
for my $f (@ARGV)
{
    if (! -e $f)
{
   system("touch \"$f\"");
}
$args .= "\"$f\" ";
}
 
if ($pid)
 {
   system("open -a /Applications/MacVim.app $args");
 } 
else
 {
   system("/Applications/MacVim.app/Contents/MacOS/MacVim $args &");
}

 
exit;
