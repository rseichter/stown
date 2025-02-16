# vim: ts=4 sw=4 noet
adoc		?= ~/.local/share/gem/ruby/3.3.0/bin/asciidoctor
adoc_opts	?= -o $@
html		?= index.html
pdf			?= stown.pdf
sources		?= stown.adoc usage.txt
targets		?= $(html) $(pdf)

.PHONY:	all clean force

all: $(targets)

$(html): $(sources)
	$(adoc) -a toc=right $(adoc_opts) $<

$(pdf): $(sources)
	#$(adoc)-pdf -a toc=auto -d article $(adoc_opts) $<
	$(adoc)-pdf -a toc=auto $(adoc_opts) $<

clean:
	rm -f $(targets)

force:	clean all
