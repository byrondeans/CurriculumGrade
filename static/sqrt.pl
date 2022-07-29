#!/usr/bin/perl
use warnings;
open(FH, '>', 'output.txt') or die $!;

my $str = "1***###1\n";
my $square_counter = 4;
for (my $i=1; $i <= 12; $i++) {#first loop decides number of questions on quiz

	$str .= "\t2!!!%%%2 \n\t\t$i 3\$\$\$\@\@3";
	for(my $j=1; $j <= 50; $j++) {#second loop decides number of questions available to randomly populate each question on the quiz: in this case 12 and 50 mean 600 questions will be generated.

		$square_counter_squared = $square_counter * $square_counter;
		$str .= "\n\t\t\t 4***\$\$\$4 q$j=What is the square root of $square_counter_squared";
		
		
		my @arr = (1,2,3,4,5);
				
		#$str .= "\n\t\t\t 4***\$\$\$4 pa$j=$random_number";
		my $pchoices_string = "";
		my $subtract_or_add_to_correct_ans = -2;
		
		for(my $k=1; $k <= 5; $k++) {
			$arr[$k - 1] = $square_counter + $subtract_or_add_to_correct_ans;
			$subtract_or_add_to_correct_ans++;
		}	
		use List::Util qw(shuffle);
                @arr = shuffle(@arr);
		use List::MoreUtils qw(first_index);
		my $index_of_correct_ans = first_index { $_ eq $square_counter } @arr;
		
		$index_of_correct_ans++;
		$str .= "\n\t\t\t 4***\$\$\$4 pa$j=$index_of_correct_ans";
	
		$str .= "\n\t\t\t 4***\$\$\$4 pchoices$j=";
		for(my $k=1; $k <= 5; $k++) {
			my $choice = $arr[$k - 1];
			$str .= "$choice";	
			if ($k < 5) {
				$str .= ";;;&&&";
			}
		}
		$str .= "\n\t\t\t 4***\$\$\$4\n\t\t 3\$\$\$\@\@3";

		$square_counter++;
	}
	$str .= "\n\t2!!!%%%2\n1***###1\n";
}
print FH $str;
