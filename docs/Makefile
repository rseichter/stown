# vim: ts=4 sw=4 noet
adoc		?= ~/.local/share/gem/ruby/3.3.0/bin/asciidoctor
adoc_opts	?= -o $@
cf_example	?= example.conf
out_html	?= index.html
out_pdf		?= stown.pdf
sources		?= stown.adoc $(cf_example) usage.txt

.PHONY:	all clean force

all: $(out_html) $(out_pdf)

$(out_html): $(sources)
	$(adoc) -a toc=right $(adoc_opts) $<

$(out_pdf): $(sources)
	$(adoc)-pdf -a toc=preamble $(adoc_opts) $<

clean:
	rm -f $(out_html) $(out_pdf)

force:	clean
	make all
