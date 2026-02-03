import React, { useState } from 'react';
import axios from 'axios';
import { motion, AnimatePresence } from 'framer-motion';
import { Search, Loader2, User, Mail, GraduationCap, ChevronRight, Sparkles } from 'lucide-react';

const API_URL = import.meta.env.VITE_API_URL || '';

const container = {
  hidden: { opacity: 0 },
  show: {
    opacity: 1,
    transition: {
      staggerChildren: 0.1
    }
  }
};

const item = {
  hidden: { opacity: 0, y: 20 },
  show: { opacity: 1, y: 0 }
};

function App() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [searched, setSearched] = useState(false);

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!query.trim()) return;

    setLoading(true);
    setSearched(true);
    try {
      const response = await axios.get(`${API_URL}/semantic-search`, {
        params: { q: query, top_k: 9 }
      });
      setResults(response.data);
    } catch (error) {
      console.error("Search failed:", error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 font-sans selection:bg-primary/20 selection:text-primary">

      {/* Navbar */}
      <nav className="fixed top-0 w-full bg-white/80 backdrop-blur-md border-b border-slate-200 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          <div className="flex items-center space-x-2 cursor-pointer" onClick={() => { setSearched(false); setQuery(''); }}>
            <div className="bg-primary/10 p-2 rounded-lg">
              <Sparkles className="h-6 w-6 text-primary" />
            </div>
            <span className="font-bold text-xl tracking-tight">Faculty<span className="text-primary">Search</span></span>
          </div>
        </div>
      </nav>

      <main className="pt-24 pb-12 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto min-h-[calc(100vh-4rem)] flex flex-col">

        {/* Hero & Search Section */}
        <motion.div
          layout
          initial={false}
          className={`flex flex-col items-center justify-center transition-all duration-700 ease-[cubic-bezier(0.25,0.1,0.25,1)] ${searched ? 'pt-0 pb-8' : 'flex-1 -mt-16'}`}
        >
          <motion.div layout className="text-center max-w-2xl mx-auto mb-8">
            <motion.h1
              layout
              className={`font-bold tracking-tight text-slate-900 mb-4 ${searched ? 'text-3xl lg:text-4xl' : 'text-5xl lg:text-7xl'}`}
            >
              Find the perfect <br />
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-primary to-accent">faculty expert</span>
            </motion.h1>

            {!searched && (
              <motion.p
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.2 }}
                className="text-lg text-slate-600 mb-8"
              >
                Use the power of semantic search to find professors based on their research, expertise, and publications.
              </motion.p>
            )}
          </motion.div>

          <motion.form
            layout
            onSubmit={handleSearch}
            className={`relative w-full transition-all duration-500 ease-in-out ${searched ? 'max-w-2xl' : 'max-w-xl'}`}
          >
            <div className="relative group">
              <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                <Search className={`h-5 w-5 transition-colors duration-300 ${searched ? 'text-primary' : 'text-slate-400 group-focus-within:text-primary'}`} />
              </div>
              <input
                type="text"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Ex: 'Deep learning for computer vision'..."
                className="block w-full pl-11 pr-4 py-4 bg-white border border-slate-200 rounded-2xl text-slate-900 placeholder:text-slate-400 focus:outline-none focus:ring-4 focus:ring-primary/10 focus:border-primary shadow-[0_8px_30px_rgb(0,0,0,0.04)] transition-all duration-300 text-lg hover:shadow-[0_8px_30px_rgb(0,0,0,0.08)]"
              />
              <div className="absolute inset-y-0 right-0 pr-2 flex items-center">
                <button
                  type="submit"
                  disabled={loading}
                  className="p-2 bg-slate-900 hover:bg-primary text-white rounded-xl transition-all duration-300 disabled:opacity-50 disabled:hover:bg-slate-900 shadow-md hover:shadow-lg active:scale-95"
                >
                  {loading ? <Loader2 className="h-5 w-5 animate-spin" /> : <ChevronRight className="h-5 w-5" />}
                </button>
              </div>
            </div>
          </motion.form>
        </motion.div>

        {/* Results Section */}
        <div className="flex-1 w-full">
          {searched && !loading && results.length === 0 && (
            <motion.div
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              className="text-center py-12"
            >
              <div className="bg-slate-100 rounded-full h-16 w-16 flex items-center justify-center mx-auto mb-4">
                <Search className="h-8 w-8 text-slate-400" />
              </div>
              <h3 className="text-lg font-semibold text-slate-900">No faculty found</h3>
              <p className="text-slate-500">Try adjusting your search terms.</p>
            </motion.div>
          )}

          {results.length > 0 && (
            <motion.div
              variants={container}
              initial="hidden"
              animate="show"
              className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"
            >
              <AnimatePresence mode='popLayout'>
                {results.map((faculty) => (
                  <motion.div
                    key={faculty.id}
                    variants={item}
                    layout
                    whileHover={{ scale: 1.02, y: -5 }}
                    className="group relative bg-white rounded-2xl p-6 border border-slate-200 shadow-sm hover:shadow-[0_20px_40px_-5px_rgb(0,0,0,0.1)] hover:border-primary/20 transition-all duration-300 flex flex-col h-full"
                  >
                    <div className="absolute top-4 right-4 z-10">
                      <div className="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-semibold bg-green-50 text-green-700 border border-green-100">
                        {Math.round(faculty.similarity * 100)}% Match
                      </div>
                    </div>

                    <div className="flex items-center space-x-4 mb-4">
                      <div className="shrink-0">
                        {faculty.image_url && faculty.image_url !== "N/A" ? (
                          <div className="h-14 w-14 rounded-full overflow-hidden shadow-md border-2 border-white">
                            <img
                              src={faculty.image_url}
                              alt={faculty.name}
                              className="h-full w-full object-cover"
                              onError={(e) => {
                                e.target.style.display = 'none';
                                e.target.nextSibling.style.display = 'flex';
                              }}
                            />
                            <div className="hidden h-full w-full bg-gradient-to-br from-primary to-accent items-center justify-center text-white">
                              <span className="font-bold text-lg">{faculty.name.charAt(0)}</span>
                            </div>
                          </div>
                        ) : (
                          <div className="h-14 w-14 rounded-full bg-gradient-to-br from-primary to-accent flex items-center justify-center text-white shadow-md border-2 border-white">
                            <span className="font-bold text-lg">{faculty.name.charAt(0)}</span>
                          </div>
                        )}
                      </div>
                      <div className="min-w-0">
                        <h3 className="text-lg font-bold text-slate-900 leading-tight group-hover:text-primary transition-colors truncate">
                          {faculty.name}
                        </h3>
                        <p className="text-sm text-slate-500 mt-1 truncate">Faculty Member</p>
                      </div>
                    </div>

                    <div className="space-y-3 mb-6 flex-grow">
                      <div className="flex items-start space-x-3 text-sm text-slate-600">
                        <Mail className="h-4 w-4 mt-0.5 text-slate-400 shrink-0" />
                        <span className="break-all hover:text-primary transition-colors cursor-pointer" title="Copy email" onClick={() => navigator.clipboard.writeText(faculty.email)}>
                          {faculty.email}
                        </span>
                      </div>
                      <div className="flex items-start space-x-3 text-sm text-slate-600">
                        <GraduationCap className="h-4 w-4 mt-0.5 text-slate-400 shrink-0" />
                        <span className="line-clamp-2">{faculty.qualification}</span>
                      </div>
                    </div>

                    <div className="pt-4 border-t border-slate-100 flex justify-end items-center mt-auto">
                      <a
                        href={faculty.profile_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="inline-flex items-center space-x-2 text-sm font-medium text-slate-600 hover:text-primary transition-colors group/link px-3 py-2 rounded-lg hover:bg-primary/5"
                      >
                        <span>View Profile</span>
                        <ChevronRight className="h-4 w-4 transition-transform group-hover/link:translate-x-1" />
                      </a>
                    </div>
                  </motion.div>
                ))}
              </AnimatePresence>
            </motion.div>
          )}
        </div>
      </main>
    </div>
  );
}

export default App;
