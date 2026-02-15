# vim: ts=4 sw=4 noet
ad_opts		?= -v -o $@
html		?= index.html
pdf			?= stown.pdf
sources		?= $(shell echo *.adoc *.txt)
targets		?= $(html) $(pdf)

.PHONY:	all clean exa force

all: $(targets)

$(html): $(sources)
	asciidoctor -a toc=right $(ad_opts) $<

$(pdf): $(sources)
	asciidoctor-pdf -a toc=auto -a title-page $(ad_opts) $<

tmp		:= exa.tmp
tree	:= tree -a --noreport mike >$(tmp)
exa:
	find mike/zulu -type l -delete
	$(tree)
	catto -r before.txt $(tmp)
	env PYTHONPATH=../src stown -f -i '\.txt$$' -l info mike/zulu mike/{alpha,bravo}
	$(tree)
	catto -r after.txt $(tmp)

clean:
	rm -f $(targets)

force:	clean all
