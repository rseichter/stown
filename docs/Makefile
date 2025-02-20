# vim: ts=4 sw=4 noet
adoc		?= ~/.local/share/gem/ruby/3.3.0/bin/asciidoctor
adoc_opts	?= -v -o $@
html		?= index.html
pdf			?= stown.pdf
sources		?= $(shell echo *.adoc *.txt)
targets		?= $(html) $(pdf)

.PHONY:	all clean exa force

all: $(targets)

$(html): $(sources)
	$(adoc) -a toc=right $(adoc_opts) $<

$(pdf): $(sources)
	$(adoc)-pdf -a toc=auto -a title-page $(adoc_opts) $<

tmp		:= exa.tmp
tree	:= tree -a --noreport mike >$(tmp)
exa:
	find mike/zulu -type l -delete
	$(tree)
	catto -r before.txt $(tmp)
	stown -f -l warn mike/zulu mike/{alpha,bravo}
	$(tree)
	catto -r after.txt $(tmp)

clean:
	rm -f $(targets)

force:	clean all
